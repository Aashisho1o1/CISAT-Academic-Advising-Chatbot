# 🚀 Quick Start: LandingAI Integration

## ✅ Setup Complete!

Your academic advising platform now has **AI-powered document extraction** using LandingAI's ADE API!

---

## 🎯 What's Been Implemented

### Backend (`backend/`)
✅ **landingai_service.py** - Service module for LandingAI operations
- `extract_courses()` - Main extraction function
- `parse_document_to_markdown()` - Parse PDF/Excel/CSV to text
- `extract_courses_async()` - For large files (>50 pages)
- `get_job_status()` - Check async job progress

✅ **app.py** - Updated Flask routes
- `/api/upload` - Smart upload with automatic extraction
- `/api/upload/async` - Async upload for large files
- `/api/upload/status/<job_id>` - Check async status

✅ **.env** - API key configured
- `VISION_AGENT_API_KEY` is set and ready

✅ **requirements.txt** - Dependencies installed
- `landingai-ade==0.21.2`
- `pydantic==2.12.4`

### Frontend (`frontend/src/`)
✅ **api.ts** - New API functions
- `uploadFile()` - Upload with extraction
- `uploadFileAsync()` - Async upload
- `checkUploadStatus()` - Status checker

✅ **components/AdvisingSheet.tsx** - Enhanced UI
- Beautiful upload interface with status messages
- Real-time extraction progress
- Display extracted course data
- Automatic refresh of journey map

✅ **Sample Test File**
- `backend/uploads/sample_advising_sheet.txt` - Test with 13 courses

---

## 🧪 Test the Integration

### Method 1: Quick Test Script

```bash
cd backend
source venv/bin/activate  # or: . venv/bin/activate
python test_landingai.py
```

This will:
1. Load the sample advising sheet
2. Extract courses using LandingAI
3. Show you the extracted JSON data
4. Verify your API key works

### Method 2: Test in Web App

1. **Start Backend** (if not running):
```bash
cd backend
source venv/bin/activate
python app.py
```

2. **Start Frontend** (if not running):
```bash
cd frontend
npm start
```

3. **Test Upload**:
   - Login (username: `test`, password: `test`)
   - Go to "Advising Sheet" page
   - Upload `backend/uploads/sample_advising_sheet.txt`
   - Watch the magic! ✨

---

## 📊 What You'll See

### During Upload:
```
⏳ Processing...
Uploading file...
Upload successful! Extracting course data...
```

### After Extraction:
```
✅ Success! Found 13 courses. Created 10, Updated 3.

📊 Extracted Data:
Student: Jane Smith
Student ID: 12345678
Program: Master of Science in Information Systems (MSIS)
Courses Found: 13

View Course Details ▼
  • CS501: Advanced Database Systems (3 credits) - Grade: A - Prof: Dr. Anderson ✅
  • IT502: Systems Analysis and Design (3 credits) - Grade: A- - Prof: Dr. Williams ✅
  • CS504: Machine Learning Fundamentals (3 credits) - Grade: A - Prof: Dr. Chen ✅
  ... and 10 more
```

---

## 🎨 How It Works

```
┌─────────────────────┐
│ Student Uploads     │
│ PDF/Excel/CSV       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Flask Backend       │
│ /api/upload         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ LandingAI Service   │
│ 1. Parse Document   │
│ 2. Extract Schema   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Pydantic Schema:    │
│ - course_code       │
│ - course_name       │
│ - credits           │
│ - professor         │
│ - grade             │
│ - completed         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Database            │
│ - Create Courses    │
│ - Add UserCourses   │
│ - Mark Completed    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Journey Map 🗺️       │
│ - Green: Complete   │
│ - Red: Pending      │
│ - Arrows: Prereqs   │
└─────────────────────┘
```

---

## 📁 Supported File Formats

✅ **PDF** - Scanned or digital transcripts
✅ **Excel** (.xlsx, .xls) - Spreadsheet format
✅ **CSV** - Comma-separated values
✅ **Text** (.txt) - Plain text format

---

## 🔑 Extraction Schema

The AI looks for these fields:

```python
CourseData:
  - course_code: "CS501"
  - course_name: "Advanced Database Systems"
  - credits: 3
  - professor: "Dr. Anderson" (optional)
  - grade: "A" (optional)
  - semester: "Fall 2023" (optional)
  - completed: true

AcademicSheet:
  - courses: [CourseData, ...]
  - student_name: "Jane Smith" (optional)
  - student_id: "12345678" (optional)
  - program: "MSIS" (optional)
```

---

## 🛠️ Customization

### Add More Fields

Edit `backend/landingai_service.py`:

```python
class CourseData(BaseModel):
    course_code: str = Field(...)
    course_name: str = Field(...)
    credits: int = Field(...)
    
    # ADD YOUR CUSTOM FIELDS:
    instructor_email: Optional[str] = Field(description="Professor email", default=None)
    textbook: Optional[str] = Field(description="Required textbook", default=None)
    room_number: Optional[str] = Field(description="Classroom location", default=None)
```

### Change Extraction Model

In `landingai_service.py`, change the model:

```python
def parse_document_to_markdown(self, file_path: Path, model: str = "dpt-2-latest"):
    # Options: "dpt-2-latest", "dpt-1", etc.
```

---

## 💰 Cost Tracking

LandingAI charges per page/document:
- **Free Tier**: ~100-500 pages/month
- **Cost**: ~$0.01-0.10 per page

### Check Usage:
1. Visit https://landing.ai/
2. Go to your dashboard
3. View API usage statistics

---

## 🐛 Troubleshooting

### Error: "Invalid API Key"
```bash
# Check your .env file
cat backend/.env | grep VISION_AGENT_API_KEY

# Should show your key (base64 encoded string)
```

### Error: "Failed to parse document"
- Ensure file is not corrupted
- Check file size (< 10MB for sync, < 50MB for async)
- Verify file format is supported

### Error: "No courses found"
- LandingAI might not recognize the document structure
- Try a clearer format (use the sample as template)
- Check if document has actual course information

### Extraction Too Slow?
Use async upload for large files:

```typescript
// In frontend/src/components/AdvisingSheet.tsx
import { uploadFileAsync, checkUploadStatus } from '../api';

// Use uploadFileAsync() instead of uploadFile()
const response = await uploadFileAsync(file);
const jobId = response.data.job_id;

// Poll for status
const statusResponse = await checkUploadStatus(jobId);
```

---

## 📈 Next Steps

### Enhance the Feature:
1. **Add prerequisite detection** - Extract course dependencies
2. **GPA calculation** - Auto-calculate from grades
3. **Degree progress** - Show % completion
4. **Course recommendations** - Suggest next courses
5. **Multi-file upload** - Upload multiple transcripts

### Production Deployment:
1. **Error handling** - Better user messages
2. **Rate limiting** - Prevent abuse
3. **File validation** - Check size/format before upload
4. **Caching** - Store extracted data, don't re-parse
5. **Background jobs** - Use Celery/Redis for async processing

---

## 🎉 You're All Set!

Your academic advising platform now has:
- ✅ AI-powered document extraction
- ✅ Automatic course population
- ✅ Smart journey map updates
- ✅ Beautiful UI with progress indicators

**Try it now:**
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python app.py

# Terminal 2: Frontend
cd frontend && npm start

# Then visit: http://localhost:3000
```

Upload a transcript and watch the magic happen! 🚀✨

---

## 📞 Support

- **LandingAI Docs**: https://landing.ai/docs
- **LandingAI Support**: support@landing.ai
- **API Reference**: https://docs.landing.ai/

---

**Happy Coding!** 🎓💻
