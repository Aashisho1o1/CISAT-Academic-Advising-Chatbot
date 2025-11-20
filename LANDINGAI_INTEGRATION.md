# 🚀 LandingAI ADE Integration Guide

## 📋 **What We're Building**

Integrate LandingAI's Automated Data Extraction (ADE) API to:
1. **Upload** - Student uploads academic advising sheet (PDF/Excel/CSV)
2. **Extract** - LandingAI extracts course data (code, name, professor, credits, grade)
3. **Populate** - Automatically create courses and mark completed ones
4. **Visualize** - Journey map updates with extracted data

---

## 🔑 **Step 1: Get LandingAI API Key**

1. Sign up at https://landing.ai/
2. Get your API key from dashboard
3. Add to backend `.env` file:

```bash
# backend/.env
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///advising.db
VISION_AGENT_API_KEY=your-landingai-api-key-here
```

---

## 📦 **Step 2: Install LandingAI Python SDK**

```bash
cd /Users/aahishsunar/Desktop/Academic\ Advising\ Chatbot
source venv/bin/activate
pip install landingai-ade
pip freeze > backend/requirements.txt
```

---

## 🏗️ **Step 3: Backend Changes**

### **A. Create LandingAI Service Module**

Create a new file: `backend/landingai_service.py`

```python
"""
LandingAI Service - Handles document parsing and data extraction
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from landingai_ade import LandingAIADE
from landingai_ade.lib import pydantic_to_json_schema
from pydantic import BaseModel, Field


# Define the schema for course extraction
class CourseData(BaseModel):
    """Schema for extracting course information from academic documents"""
    course_code: str = Field(description="Course code (e.g., CS101, MATH201)")
    course_name: str = Field(description="Full course name")
    credits: int = Field(description="Number of credits (1-5)")
    professor: Optional[str] = Field(description="Professor name", default=None)
    grade: Optional[str] = Field(description="Letter grade (A, B+, C, etc.)", default=None)
    semester: Optional[str] = Field(description="Semester taken (e.g., Fall 2024)", default=None)
    completed: bool = Field(description="Whether the course is completed", default=False)


class AcademicSheet(BaseModel):
    """Schema for extracting all courses from academic sheet"""
    courses: List[CourseData] = Field(description="List of all courses")
    student_name: Optional[str] = Field(description="Student name", default=None)
    student_id: Optional[str] = Field(description="Student ID", default=None)
    program: Optional[str] = Field(description="Degree program (e.g., MSIS)", default=None)


class LandingAIService:
    """Service class for LandingAI ADE operations"""
    
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
        Parse document (PDF/Excel/CSV) to markdown format
        
        Args:
            file_path: Path to the document file
            model: LandingAI model to use
        
        Returns:
            Parsed markdown content
        """
        try:
            # Use LandingAI's parse endpoint
            response = self.client.parse(
                document=file_path,
                model=model
            )
            
            # Extract text chunks and combine
            markdown_text = "\n\n".join([chunk.text for chunk in response.chunks])
            return markdown_text
        
        except Exception as e:
            raise Exception(f"Failed to parse document: {str(e)}")
    
    def extract_courses(self, file_path: Path) -> Dict:
        """
        Extract structured course data from academic advising sheet
        
        This is the MAIN function you'll call from Flask routes
        
        Args:
            file_path: Path to uploaded file (PDF/Excel/CSV)
        
        Returns:
            Dictionary with extracted course data
        """
        try:
            # Step 1: Parse document to markdown
            markdown_content = self.parse_document_to_markdown(file_path)
            
            # Step 2: Save markdown to temp file (LandingAI extract needs markdown)
            temp_md_path = file_path.with_suffix('.md')
            temp_md_path.write_text(markdown_content)
            
            # Step 3: Extract structured data using schema
            schema = pydantic_to_json_schema(AcademicSheet)
            response = self.client.extract(
                schema=schema,
                markdown=temp_md_path
            )
            
            # Step 4: Clean up temp file
            temp_md_path.unlink()
            
            # Step 5: Convert response to dict
            # LandingAI returns the extracted data matching your schema
            return response.to_dict() if hasattr(response, 'to_dict') else response
        
        except Exception as e:
            raise Exception(f"Failed to extract courses: {str(e)}")
    
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
    
    # Test with a sample file
    test_file = Path("uploads/sample_advising_sheet.pdf")
    
    if test_file.exists():
        print("Extracting courses from:", test_file)
        result = service.extract_courses(test_file)
        print("Extracted data:", result)
    else:
        print("Test file not found. Upload a file first.")
```

---

### **B. Update `backend/app.py` - Modify Upload Route**

Find your `/api/upload` route and update it:

```python
from landingai_service import LandingAIService

# Initialize LandingAI service (do this near other initializations)
landingai_service = LandingAIService()

@app.route('/api/upload', methods=['POST'])
@login_required
def upload():
    """
    Upload advising sheet and extract course data using LandingAI
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Save file
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(app.root_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Extract courses using LandingAI
            extracted_data = landingai_service.extract_courses(Path(filepath))
            
            # Save to database
            advising_sheet = AdvisingSheet(
                user_id=current_user.id,
                filename=filename,
                filepath=filepath,
                parsed_data=json.dumps(extracted_data)  # Store extracted data
            )
            db.session.add(advising_sheet)
            
            # Automatically create courses and mark user courses
            if 'courses' in extracted_data:
                for course_data in extracted_data['courses']:
                    # Check if course exists
                    course = Course.query.filter_by(code=course_data['course_code']).first()
                    
                    # Create course if doesn't exist
                    if not course:
                        course = Course(
                            code=course_data['course_code'],
                            name=course_data['course_name'],
                            credits=course_data['credits'],
                            required=True,  # Default to required
                            prerequisites='[]'  # Can enhance later
                        )
                        db.session.add(course)
                        db.session.flush()  # Get course.id
                    
                    # Add to user's courses
                    user_course = UserCourse.query.filter_by(
                        user_id=current_user.id,
                        course_id=course.id
                    ).first()
                    
                    if not user_course:
                        user_course = UserCourse(
                            user_id=current_user.id,
                            course_id=course.id,
                            completed=course_data.get('completed', False),
                            grade=course_data.get('grade', '')
                        )
                        db.session.add(user_course)
                    else:
                        # Update existing
                        user_course.completed = course_data.get('completed', False)
                        user_course.grade = course_data.get('grade', '')
            
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded and courses extracted successfully',
                'id': advising_sheet.id,
                'extracted_data': extracted_data
            }), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to process file: {str(e)}'}), 500
    
    return jsonify({'error': 'File not allowed'}), 400
```

---

### **C. Add New Route for Job Status (Optional - for large files)**

```python
@app.route('/api/upload/async', methods=['POST'])
@login_required
def upload_async():
    """
    Upload large file and create async extraction job
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Create async job
        job_id = landingai_service.extract_courses_async(Path(filepath))
        
        return jsonify({
            'message': 'File uploaded, extraction in progress',
            'job_id': job_id
        }), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/status/<job_id>', methods=['GET'])
@login_required
def upload_status(job_id: str):
    """
    Check status of async extraction job
    """
    try:
        status = landingai_service.get_job_status(job_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🎨 **Step 4: Frontend Changes**

### **A. Update `frontend/src/api.ts`**

Add the new upload endpoint return type:

```typescript
export const uploadFile = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// For large files (optional)
export const uploadFileAsync = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/async', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const checkUploadStatus = (jobId: string) => {
  return api.get(`/upload/status/${jobId}`);
};
```

---

### **B. Update `frontend/src/components/AdvisingSheet.tsx`**

Enhance the file upload section to show extracted data:

```tsx
const [extractedData, setExtractedData] = useState<any>(null);
const [uploadStatus, setUploadStatus] = useState('');

const handleFileUpload = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!file) return;
  
  setUploadStatus('Uploading...');
  
  try {
    const response = await uploadFile(file);
    setUploadStatus('Upload successful! Extracting data...');
    
    // Show extracted data
    if (response.data.extracted_data) {
      setExtractedData(response.data.extracted_data);
      alert(`Successfully extracted ${response.data.extracted_data.courses?.length || 0} courses!`);
    }
    
    setFile(null);
    setUploadStatus('');
    
    // Refresh user courses to show newly added ones
    fetchUserCourses();
  } catch (error) {
    console.error('Error uploading file:', error);
    setUploadStatus('Upload failed. Please try again.');
  }
};

// In JSX, add a section to display extracted data
{extractedData && (
  <div style={{ marginTop: '20px', padding: '15px', background: '#f0f0f0', borderRadius: '8px' }}>
    <h4>Extracted Data:</h4>
    {extractedData.student_name && <p><strong>Student:</strong> {extractedData.student_name}</p>}
    {extractedData.program && <p><strong>Program:</strong> {extractedData.program}</p>}
    <p><strong>Courses Found:</strong> {extractedData.courses?.length || 0}</p>
    <button onClick={() => setExtractedData(null)}>Close</button>
  </div>
)}
```

---

## 🧪 **Step 5: Testing the Integration**

### **A. Prepare Test Documents**

Create sample files in `backend/uploads/` for testing:

**sample_advising_sheet.txt:**
```
Student Name: John Doe
Student ID: 123456
Program: MSIS

Courses Completed:
- CS101: Introduction to Computer Science, Credits: 3, Grade: A, Professor: Dr. Smith
- MATH201: Calculus I, Credits: 4, Grade: B+, Professor: Dr. Johnson
- CS201: Data Structures, Credits: 4, Grade: A-, Professor: Dr. Williams

Courses In Progress:
- CS301: Algorithms, Credits: 3, Professor: Dr. Brown
- DB401: Database Systems, Credits: 3, Professor: Dr. Davis
```

### **B. Test Locally**

```python
# backend/test_landingai.py
from pathlib import Path
from landingai_service import LandingAIService

service = LandingAIService()

# Test with sample file
test_file = Path("uploads/sample_advising_sheet.txt")
result = service.extract_courses(test_file)

print("Extracted Data:")
print(json.dumps(result, indent=2))
```

Run test:
```bash
cd backend
python test_landingai.py
```

---

## 📊 **How Data Flows**

```
┌─────────────┐
│   Student   │
│  Uploads    │
│   PDF/CSV   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Flask Backend      │
│  /api/upload        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  LandingAI Service  │
│  1. Parse document  │
│  2. Extract schema  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Extracted JSON:    │
│  {                  │
│    courses: [       │
│      {              │
│        code: CS101  │
│        name: Intro  │
│        credits: 3   │
│        grade: A     │
│      }              │
│    ]                │
│  }                  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Database           │
│  - Create courses   │
│  - Add user_courses │
│  - Mark completed   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Journey Map        │
│  - Green: Complete  │
│  - Red: Pending     │
│  - Arrows: Prereqs  │
└─────────────────────┘
```

---

## 🎯 **Expected Output Example**

When you upload a PDF, LandingAI returns:

```json
{
  "student_name": "John Doe",
  "student_id": "123456",
  "program": "MSIS",
  "courses": [
    {
      "course_code": "CS101",
      "course_name": "Introduction to Computer Science",
      "credits": 3,
      "professor": "Dr. Smith",
      "grade": "A",
      "semester": "Fall 2024",
      "completed": true
    },
    {
      "course_code": "CS201",
      "course_name": "Data Structures",
      "credits": 4,
      "professor": "Dr. Williams",
      "grade": "A-",
      "semester": "Spring 2025",
      "completed": true
    },
    {
      "course_code": "CS301",
      "course_name": "Algorithms",
      "credits": 3,
      "professor": "Dr. Brown",
      "grade": null,
      "semester": null,
      "completed": false
    }
  ]
}
```

---

## 🚨 **Error Handling**

LandingAI can fail for several reasons:

```python
try:
    result = service.extract_courses(file_path)
except Exception as e:
    if "API key" in str(e):
        return jsonify({'error': 'Invalid LandingAI API key'}), 401
    elif "timeout" in str(e):
        return jsonify({'error': 'Request timeout, try smaller file'}), 504
    elif "rate limit" in str(e):
        return jsonify({'error': 'Rate limit exceeded, try again later'}), 429
    else:
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500
```

---

## 💰 **Cost Considerations**

LandingAI charges per page/document. Check their pricing:
- Free tier: Usually 100-500 pages/month
- Paid tiers: ~$0.01-0.10 per page

**Optimization tips:**
1. Cache extracted data (don't re-parse same file)
2. Use async jobs for large files
3. Validate file size before sending to API

---

## 🔄 **Delete LandingAI Reference Repo (After Integration)**

```bash
cd /Users/aahishsunar/Desktop
rm -rf landingai-reference-temp
```

---

## 📝 **Summary Checklist**

- [ ] Get LandingAI API key
- [ ] Install `landingai-ade` package
- [ ] Create `landingai_service.py`
- [ ] Update `/api/upload` route
- [ ] Update frontend `api.ts`
- [ ] Update `AdvisingSheet.tsx` to show extracted data
- [ ] Test with sample documents
- [ ] Handle errors gracefully
- [ ] Deploy to production

---

## 🎓 **Key Concepts Learned**

1. **Document Parsing** - Converting PDF/Excel to structured data
2. **Schema Definition** - Using Pydantic to define extraction structure
3. **API Integration** - Calling external services from Flask
4. **Async Processing** - Handling long-running tasks
5. **Data Transformation** - Backend data → Frontend display

This integration will make your app **WAY more powerful** - students just upload their advising sheet and boom, everything is automatically filled in! 🚀
