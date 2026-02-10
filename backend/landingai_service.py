
"""
LandingAI Service - Handles document parsing and data extraction
Smart extraction for academic planning sheets with table structure
"""
import json
import logging
import os
import re
from html import unescape
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)


# Enhanced schema that understands table structure
class CourseData(BaseModel):
    """Schema for extracting course from academic planning sheet table"""
    course_code: str = Field(
        description="Course code from COURSE column (e.g., IST 302, IST 303, CS101)"
    )
    course_title: str = Field(
        description="Course title from TITLE column (e.g., Databases, Software Development)"
    )
    units: int = Field(
        description="Credit units from UNITS column (typically 4)",
        default=4
    )
    waived_transferred: Optional[str] = Field(
        description="Waived or transferred status from WAIVED/TRANSFERRED column",
        default=None
    )
    semester_taken: Optional[str] = Field(
        description="Semester from SEMESTER TAKEN column (e.g., Fall 2025, Spring 2026)",
        default=None
    )
    notes: Optional[str] = Field(
        description="Additional notes from NOTES column (e.g., PR: SQL, Prerequisites)",
        default=None
    )
    section: Optional[str] = Field(
        description="Section type: CORE, CONCENTRATION, or ELECTIVE",
        default=None
    )
    completed: bool = Field(
        description="True if SEMESTER TAKEN has a value (indicating course is planned/completed)",
        default=False
    )


class AcademicPlanningSheet(BaseModel):
    """Schema for complete academic planning sheet with table structure"""
    student_name: Optional[str] = Field(
        description="Student name from Student Name field at top of document",
        default=None
    )
    advisor: Optional[str] = Field(
        description="Advisor name from Advisor field",
        default=None
    )
    id_number: Optional[str] = Field(
        description="Student ID from ID Number field",
        default=None
    )
    program: str = Field(
        description="Degree program (e.g., MSIST, MSIS)",
        default="MSIST"
    )
    core_courses: List[CourseData] = Field(
        description="Courses under CISAT CORE COURSES section of table",
        default=[]
    )
    concentration_courses: List[CourseData] = Field(
        description="Courses under CONCENTRATION COURSE section of table",
        default=[]
    )
    elective_courses: List[CourseData] = Field(
        description="Courses under ELECTIVE or SECOND CONCENTRATION section of table",
        default=[]
    )


class LandingAIService:
    """Service class for LandingAI ADE operations with smart table parsing"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LandingAI client
        
        Args:
            api_key: LandingAI API key (defaults to VISION_AGENT_API_KEY env var)
        """
        self.client = LandingAIADE(
            apikey=api_key or os.environ.get("VISION_AGENT_API_KEY")
        )
    
    def parse_document_to_markdown(self, file_path: Path, model: str = "dpt-2-latest") -> str:
        """
        Parse document to text using PyPDF2 (free, no API required)
        Falls back to LandingAI if PyPDF2 fails
        
        Args:
            file_path: Path to the document file
            model: Not used in PyPDF2 mode (kept for backward compatibility)
        
        Returns:
            Parsed text content
        """
        try:
            # Try PyPDF2 first (free, offline)
            logger.info("[PDF Parser] Parsing document with PyPDF2: %s", file_path)
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text_chunks = []
                
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_chunks.append(page_text)
                
                text = "\n\n".join(text_chunks)
                logger.info(
                    "[PDF Parser] Extracted %s pages, %s characters",
                    len(text_chunks),
                    len(text),
                )
                return text
        
        except ImportError:
            logger.warning("[PDF Parser] PyPDF2 not installed, falling back to LandingAI...")
            # Fallback to LandingAI if PyPDF2 not available
            return self._parse_with_landingai(file_path, model)
        
        except Exception as e:
            logger.warning("[PDF Parser] PyPDF2 failed: %s, trying LandingAI...", e)
            # Fallback to LandingAI if PyPDF2 fails
            return self._parse_with_landingai(file_path, model)
    
    def _parse_with_landingai(self, file_path: Path, model: str = "dpt-2-latest") -> str:
        """
        Parse document using LandingAI API (requires API key and credits)
        This is a fallback when PyPDF2 fails
        """
        try:
            logger.info("[LandingAI] Parsing document: %s", file_path)
            response = self.client.parse(
                document=file_path,
                model=model
            )
            
            # Extract markdown chunks and combine - use model_dump() for Pydantic v2
            chunks_text = []
            for chunk in response.chunks:
                chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk.dict()
                text = chunk_dict.get('markdown', '')
                if text.strip():
                    chunks_text.append(text)
            
            markdown_text = "\n\n".join(chunks_text)
            logger.info(
                "[LandingAI] Parsed %s chunks, %s characters",
                len(chunks_text),
                len(markdown_text),
            )
            return markdown_text
        
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    def extract_courses(self, file_path: Path) -> Dict:
        """
        Smart extraction that understands academic planning sheet table structure
        
        This is the MAIN function called from Flask routes.
        Uses PyPDF2 + regex extraction (NO API calls needed)
        
        Args:
            file_path: Path to uploaded file (PDF/Excel/CSV)
        
        Returns:
            Dictionary with extracted course data
        """
        try:
            # Step 1: Parse document to text using PyPDF2
            logger.info("[Extractor] Parsing document: %s", file_path.name)
            text_content = self.parse_document_to_markdown(file_path)
            logger.debug("[Extractor] Text preview (first 500 chars):\n%s...", text_content[:500])
            
            # Step 2: Use regex extraction (no API call)
            logger.info("[Extractor] Extracting courses using regex pattern matching...")
            courses = self._regex_extract_courses(text_content)
            
            # Step 3: Organize by section
            result = {
                'core_courses': [c for c in courses if c.get('section') == 'CORE'],
                'concentration_courses': [c for c in courses if c.get('section') == 'CONCENTRATION'],
                'elective_courses': [c for c in courses if c.get('section') == 'ELECTIVE'],
                'courses': courses
            }
            
            logger.info("[Extractor] Extracted %s total courses", len(courses))
            logger.info("  - Core: %s", len(result["core_courses"]))
            logger.info("  - Concentration: %s", len(result["concentration_courses"]))
            logger.info("  - Elective: %s", len(result["elective_courses"]))
            
            return result
        
        except Exception as e:
            logger.exception("[Extractor] Extraction failed: %s", str(e))
            raise Exception(f"Failed to extract courses: {str(e)}")
    
    def _post_process_courses(self, result: Dict, markdown: str) -> Dict:
        """
        Post-process extracted data with regex fallback for missed courses
        """
        logger.info("[LandingAI] Post-processing and validating courses...")
        
        # Count extracted courses
        all_extracted = sum([
            len(result.get('core_courses', [])),
            len(result.get('concentration_courses', [])),
            len(result.get('elective_courses', []))
        ])
        
        # If AI missed courses (expected at least 3 core courses), use regex fallback
        if all_extracted < 3:
            logger.warning(
                "[LandingAI] Low extraction count (%s), using regex fallback...",
                all_extracted,
            )
            fallback_courses = self._regex_extract_courses(markdown)
            
            # Merge with AI results (AI takes priority if exists)
            if not result.get('core_courses'):
                result['core_courses'] = [c for c in fallback_courses if c.get('section') == 'CORE']
            if not result.get('concentration_courses'):
                result['concentration_courses'] = [c for c in fallback_courses if c.get('section') == 'CONCENTRATION']
            if not result.get('elective_courses'):
                result['elective_courses'] = [c for c in fallback_courses if c.get('section') == 'ELECTIVE']
        
        # Mark courses as completed if they have semester_taken value
        for section_key in ['core_courses', 'concentration_courses', 'elective_courses']:
            for course in result.get(section_key, []):
                if isinstance(course, dict):
                    semester = course.get('semester_taken', '')
                    course['completed'] = bool(semester and semester.strip())
                    # Normalize field names for compatibility with app.py
                    if 'course_title' in course and 'course_name' not in course:
                        course['course_name'] = course['course_title']
                    if 'units' in course and 'credits' not in course:
                        course['credits'] = course['units']
        
        return result
    
    def _regex_extract_courses(self, markdown: str) -> List[Dict]:
        """
        Fallback regex-based extraction for table-structured documents
        IMPROVED: Strips HTML tags first, then finds ALL courses with semester info
        Only extracts courses that have a semester (Fall/Spring YYYY) in SEMESTER TAKEN column
        """
        # Step 1: Strip HTML tags from markdown
        clean_text = re.sub(r'<[^>]+>', ' ', markdown)  # Remove all HTML tags
        clean_text = unescape(clean_text)  # Decode HTML entities like &nbsp;
        clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
        
        courses = []
        current_section = None
        
        # Step 2: Find section boundaries in the text
        section_patterns = {
            'CORE': r'CISAT CORE COURSES',
            'CONCENTRATION': r'CONCENTRATION COURSE',
            'ELECTIVE': r'ELECTIVE or SECOND CONCENTRATION'
        }
        
        # Find section positions
        section_positions = []
        for section_type, pattern in section_patterns.items():
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                section_positions.append((match.start(), section_type))
                logger.debug(
                    "  Found section: %s at position %s",
                    section_type,
                    match.start(),
                )
        
        section_positions.sort()  # Sort by position in text
        
        # Step 3: Find ALL course patterns with semester in the text
        # Pattern 1: Full code - "IST 302 Databases 4 Fall 2025"
        # Pattern 2: Partial code - "IST Deep Learning 4 Spring 2026" (missing number)
        pattern_full = r'\b([A-Z]{2,4})\s+(\d{3})\s+([A-Za-z\s]+?)\s+(\d)\s+(Fall|Spring)\s+(\d{4})'
        pattern_partial = r'\b([A-Z]{2,4})\s+([A-Z][A-Za-z\s]+?)\s+(\d)\s+(Fall|Spring)\s+(\d{4})'
        
        # Extract courses with full codes first
        for match in re.finditer(pattern_full, clean_text, re.IGNORECASE):
            dept = match.group(1)
            number = match.group(2)
            title = match.group(3).strip()
            units = int(match.group(4))
            season = match.group(5)
            year = match.group(6)
            
            course_code = f"{dept} {number}"
            semester = f"{season} {year}"
            
            # Determine which section this course belongs to based on position
            course_pos = match.start()
            current_section = None
            for i, (pos, section_type) in enumerate(section_positions):
                if course_pos > pos:
                    current_section = section_type
                    # Check if there's a next section that would exclude this
                    if i + 1 < len(section_positions) and course_pos > section_positions[i+1][0]:
                        continue
                    break
            
            if not current_section:
                continue  # Skip courses not in any section
            
            # Extract notes if present (after semester)
            notes_match = re.search(
                rf'{re.escape(semester)}\s+(PR:[^A-Z]*(?:[A-Z]{{2,4}}\s+\d{{3}}|CHECKLIST))',
                clean_text[match.end():match.end()+100],
                re.IGNORECASE
            )
            notes = notes_match.group(1).strip() if notes_match else None
            if notes:
                notes = re.sub(r'\s+(IST|CHECKLIST).*$', '', notes).strip()
            
            course = {
                'course_code': course_code,
                'course_title': title,
                'course_name': title,
                'units': units,
                'credits': units,
                'semester_taken': semester,
                'notes': notes,
                'section': current_section,
                'completed': True
            }
            
            courses.append(course)
            logger.debug("  Extracted: %s - %s (%s)", course_code, title, semester)
        
        # Extract courses with partial codes (IST without number)
        # Only add if not already in the list (avoid duplicates)
        existing_codes = {c['course_code'] for c in courses}
        
        for match in re.finditer(pattern_partial, clean_text, re.IGNORECASE):
            dept = match.group(1)
            title = match.group(2).strip()
            units = int(match.group(3))
            season = match.group(4)
            year = match.group(5)
            
            # Skip if this looks like it matches a full course we already extracted
            if any(title.lower() in c['course_title'].lower() for c in courses):
                continue
            
            course_code = f"{dept}"  # Just department code
            semester = f"{season} {year}"
            
            # Determine section
            course_pos = match.start()
            current_section = None
            for i, (pos, section_type) in enumerate(section_positions):
                if course_pos > pos:
                    current_section = section_type
                    if i + 1 < len(section_positions) and course_pos > section_positions[i+1][0]:
                        continue
                    break
            
            if not current_section:
                continue
            
            course = {
                'course_code': course_code,
                'course_title': title,
                'course_name': title,
                'units': units,
                'credits': units,
                'semester_taken': semester,
                'notes': None,
                'section': current_section,
                'completed': True
            }
            
            courses.append(course)
            logger.debug(
                "  Extracted: %s - %s (%s) [partial code]",
                course_code,
                title,
                semester,
            )
        
        return courses
    
    def extract_courses_async(self, file_path: Path) -> str:
        """
        Create async parse job for large documents
        Returns job_id for status checking
        
        Use this for very large PDFs (>50 pages)
        """
        try:
            job = self.client.parse_jobs.create(
                document=file_path,
                model="dpt-2-latest"
            )
            return job.job_id
        except Exception as e:
            raise Exception(f"Failed to create parse job: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Dict:
        """
        Check status of async parse job
        
        Returns:
            Dictionary with job status and results (if completed)
        """
        try:
            job_status = self.client.parse_jobs.get(job_id)
            return {
                'job_id': job_id,
                'status': job_status.status,
                'result': job_status.result if job_status.status == 'completed' else None
            }
        except Exception as e:
            raise Exception(f"Failed to get job status: {str(e)}")


# Example usage (for testing)
if __name__ == "__main__":
    service = LandingAIService()
    
    # Test with the actual academic planning sheet
    test_file = Path("uploads/Academic_Planning_Sheet_MS.docx.pdf")
    
    if test_file.exists():
        print("=" * 70)
        print("TESTING SMART EXTRACTION WITH ACTUAL DOCUMENT")
        print("=" * 70)
        result = service.extract_courses(test_file)
        
        print("\n" + "=" * 70)
        print("EXTRACTION RESULTS:")
        print("=" * 70)
        print(f"Student: {result.get('student_name', 'N/A')}")
        print(f"Advisor: {result.get('advisor', 'N/A')}")
        print(f"Program: {result.get('program', 'N/A')}")
        print(f"\nTotal courses extracted: {len(result.get('courses', []))}")
        
        print("\n--- COURSES BY SECTION ---")
        for course in result.get('courses', []):
            status = '✅' if course.get('completed') else '⏳'
            print(f"\n{status} [{course.get('section', 'N/A')}] {course.get('course_code')}")
            print(f"   Title: {course.get('course_title', course.get('course_name', 'N/A'))}")
            print(f"   Units: {course.get('units', course.get('credits', 'N/A'))}")
            print(f"   Semester: {course.get('semester_taken', 'Not scheduled')}")
            if course.get('notes'):
                print(f"   Notes: {course.get('notes')}")
        
        print("\n" + "=" * 70)
    else:
        print(f"❌ Test file not found: {test_file}")
        print("Please ensure the file exists in the uploads directory.")
