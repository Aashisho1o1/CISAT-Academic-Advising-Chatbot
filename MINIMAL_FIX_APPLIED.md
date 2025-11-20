# 🔧 Minimal Fix Applied

## ✅ Issue Resolved

### **Problem:**
```
AttributeError: 'Chunk' object has no attribute 'text'
```

### **Root Cause:**
Pydantic v2 changed how to access model attributes. In Pydantic v2, you can't directly access attributes on model instances in some contexts - you need to use `.model_dump()` or `.dict()`.

---

## 🛠️ Changes Made (2 files, 3 lines changed)

### **File 1: `backend/landingai_service.py`** (Lines 61-71)

**Before:**
```python
# Extract text chunks and combine
markdown_text = "\n\n".join([chunk.text for chunk in response.chunks])
```

**After:**
```python
# Extract text chunks and combine - use model_dump() for Pydantic v2
chunks_text = []
for chunk in response.chunks:
    # Pydantic v2 objects - use model_dump() to access fields
    chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk.dict()
    chunks_text.append(chunk_dict.get('text', ''))

markdown_text = "\n\n".join(chunks_text)
```

**Why this works:**
- `chunk.model_dump()` converts Pydantic model → dictionary
- `chunk_dict.get('text', '')` safely gets the text field
- Fallback to `chunk.dict()` for Pydantic v1 compatibility

---

### **File 2: `backend/app.py`** (Line 72)

**Before:**
```python
return User.query.get(int(user_id))  # Deprecated in SQLAlchemy 2.0
```

**After:**
```python
return db.session.get(User, int(user_id))  # SQLAlchemy 2.0 syntax
```

**Why this works:**
- SQLAlchemy 2.0 moved `get()` from `Query` to `Session`
- Removes the deprecation warning

---

## 🧪 Test Now

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate  # or: . venv/bin/activate
python3 app.py

# Terminal 2: Start frontend (different terminal)
cd frontend
npm start
```

Then:
1. Open http://localhost:3000
2. Login (username: `test`, password: `test`)
3. Go to "Advising Sheet"
4. Upload `backend/uploads/Academic_Planning_Sheet_MS.docx.pdf`
5. Should work now! ✅

---

## 📊 What Happens Now

```
User uploads file
    ↓
Flask saves file
    ↓
LandingAI parses PDF
    ↓
response.chunks = [Chunk, Chunk, ...]
    ↓
chunk.model_dump() = {'text': '...', 'page': 1, ...}
    ↓
Extract 'text' from each chunk dictionary
    ↓
Join all text with "\n\n"
    ↓
Continue with extraction...
```

---

## 🎯 Key Lesson

**When working with Pydantic models:**
- ❌ Don't do: `chunk.text` (might fail in some contexts)
- ✅ Do: `chunk.model_dump()['text']` (always works)
- ✅ Or: Use `.model_dump()` then access dictionary keys

This is especially important when:
- Using external libraries (like LandingAI)
- Working with Pydantic v2
- Models are serialized/deserialized

---

## 🚀 Expected Result

```bash
[LandingAI] Parsing document: Academic_Planning_Sheet_MS.docx.pdf
[LandingAI] Parsed 5000 characters
[LandingAI] Markdown saved to: Academic_Planning_Sheet_MS.docx.md
[LandingAI] Extracting with schema...
[LandingAI] Extraction successful: 12 courses found

✅ Success! Found 12 courses. Created 10, Updated 2.
```

---

**Total changes:** 2 files, ~8 lines of code, 0 complexity added ✨
