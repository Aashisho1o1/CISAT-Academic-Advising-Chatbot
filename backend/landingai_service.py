
"""
LandingAI Service - Handles document parsing and data extraction
Smart extraction for academic planning sheets with table structure
"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


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
        Parse document to markdown, preserving table structure
        
        Args:
            file_path: Path to the document file
            model: LandingAI model to use
        
        Returns:
            Parsed markdown content
        """
        try:
            print(f"[LandingAI] Parsing document: {file_path}")
            response = self.client.parse(
                document=file_path,
                model=model
            )
            
            # Extract text chunks and combine - use model_dump() for Pydantic v2
            chunks_text = []
            for chunk in response.chunks:
                # Pydantic v2 objects - use model_dump() to access fields
                chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk.dict()
                text = chunk_dict.get('text', '')
                if text.strip():  # Only add non-empty chunks
                    chunks_text.append(text)
            
            markdown_text = "\n\n".join(chunks_text)
            print(f"[LandingAI] Parsed {len(chunks_text)} chunks, {len(markdown_text)} characters")
            return markdown_text
        
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    def extract_courses(self, file_path: Path) -> Dict:
        """
        Smart extraction that understands academic planning sheet table structure
        
        This is the MAIN function called from Flask routes.
        Uses enhanced prompting and regex fallback to extract course data.
        
        Args:
            file_path: Path to uploaded file (PDF/Excel/CSV)
        
        Returns:
            Dictionary with extracted course data
        """
        try:
            # Step 1: Parse document to markdown
            print(f"[LandingAI] Smart parsing document: {file_path.name}")
            markdown_content = self.parse_document_to_markdown(file_path)
            
            # Step 2: Save markdown for extraction
            temp_md_path = file_path.with_suffix('.md')
            temp_md_path.write_text(markdown_content)
            print(f"[LandingAI] Markdown preview (first 500 chars):\n{markdown_content[:500]}...")
            
            # Step 3: Extract with enhanced schema
            schema = pydantic_to_json_schema(AcademicPlanningSheet)
            
            print(f"[LandingAI] Extracting structured data with enhanced schema...")
            print(f"[LandingAI] Schema type: {type(schema)}")
            
            # LandingAI extract method accepts the schema directly
            response = self.client.extract(
                schema=schema,
                markdown=temp_md_path
            )
            
            # Step 4: Convert response to dict
            if hasattr(response, 'data'):
                result = response.data if isinstance(response.data, dict) else response.data.model_dump()
            elif hasattr(response, 'model_dump'):
                result = response.model_dump()
            elif isinstance(response, dict):
                result = response
            else:
                result = json.loads(json.dumps(response, default=str))
            
            # Step 5: Post-process and validate with regex fallback
            result = self._post_process_courses(result, markdown_content)
            
            # Step 6: Clean up temp file
            temp_md_path.unlink()
            
            # Step 7: Combine all courses into single list for backward compatibility with app.py
            all_courses = []
            for section_key in ['core_courses', 'concentration_courses', 'elective_courses']:
                section_courses = result.get(section_key, [])
                if isinstance(section_courses, list):
                    all_courses.extend(section_courses)
            
            result['courses'] = all_courses
            
            print(f"[LandingAI] ✅ Extracted {len(all_courses)} total courses")
            print(f"  - Core: {len(result.get('core_courses', []))}")
            print(f"  - Concentration: {len(result.get('concentration_courses', []))}")
            print(f"  - Elective: {len(result.get('elective_courses', []))}")
            
            return result
        
        except Exception as e:
            print(f"[LandingAI] ❌ Extraction failed: {str(e)}")
            raise Exception(f"Failed to extract courses: {str(e)}")
    
    def _post_process_courses(self, result: Dict, markdown: str) -> Dict:
        """
        Post-process extracted data with regex fallback for missed courses
        """
        print("[LandingAI] Post-processing and validating courses...")
        
        # Count extracted courses
        all_extracted = sum([
            len(result.get('core_courses', [])),
            len(result.get('concentration_courses', [])),
            len(result.get('elective_courses', []))
        ])
        
        # If AI missed courses (expected at least 3 core courses), use regex fallback
        if all_extracted < 3:
            print(f"[LandingAI] ⚠️ Low extraction count ({all_extracted}), using regex fallback...")
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
        Looks for patterns like: IST 302 | Databases | 4 | | Fall 2025 |
        """
        courses = []
        current_section = None
        
        # Detect section headers
        section_patterns = {
            'CORE': r'CISAT CORE COURSES|CORE COURSES',
            'CONCENTRATION': r'CONCENTRATION COURSE',
            'ELECTIVE': r'ELECTIVE|SECOND CONCENTRATION'
        }
        
        lines = markdown.split('\n')
        
        for i, line in enumerate(lines):
            # Check for section headers
            for section_type, pattern in section_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    current_section = section_type
                    print(f"  Found section: {section_type}")
                    break
            
            # Look for course code patterns: IST 302, IST302, CS101, etc.
            course_match = re.search(r'\b([A-Z]{2,4}\s*\d{3})\b', line, re.IGNORECASE)
            if course_match and current_section:
                course_code = re.sub(r'\s+', ' ', course_match.group(1)).strip()  # Normalize spacing
                
                # Try to extract other fields from the same line (table row)
                # Table format: COURSE | TITLE | UNITS | WAIVED | SEMESTER | NOTES
                parts = [p.strip() for p in line.split('|')]
                
                title = ''
                units = 4
                semester = None
                notes = None
                
                if len(parts) >= 2:
                    title = parts[1]
                if len(parts) >= 3:
                    units_match = re.search(r'\d+', parts[2])
                    if units_match:
                        units = int(units_match.group())
                if len(parts) >= 5:
                    semester = parts[4] if parts[4] else None
                if len(parts) >= 6:
                    notes = parts[5] if parts[5] else None
                
                # If title not found in same line, try next line
                if not title and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not re.search(r'\b[A-Z]{2,4}\s*\d{3}\b', next_line):
                        title = next_line
                
                course = {
                    'course_code': course_code,
                    'course_title': title or f"Course {course_code}",
                    'course_name': title or f"Course {course_code}",  # Compatibility
                    'units': units,
                    'credits': units,  # Compatibility
                    'semester_taken': semester,
                    'notes': notes,
                    'section': current_section,
                    'completed': bool(semester)
                }
                
                courses.append(course)
                print(f"  Extracted: {course_code} - {title[:30]}... ({semester or 'not scheduled'})")
        
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
