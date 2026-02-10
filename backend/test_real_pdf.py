"""Test extraction with the actual PDF that worked in LandingAI dashboard"""
import os
from pathlib import Path
from dotenv import load_dotenv
from landingai_service import LandingAIService

load_dotenv()

# Initialize service
service = LandingAIService()

# Test with the actual PDF
test_file = Path("uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf")

print("=" * 60)
print("TESTING WITH ACTUAL PDF")
print("=" * 60)
print(f"✓ File: {test_file}")
print(f"✓ Size: {test_file.stat().st_size} bytes")
print()

try:
    print("🚀 Starting extraction...")
    print("-" * 60)
    
    result = service.extract_courses(test_file)
    
    print("\n" + "=" * 60)
    print("✅ EXTRACTION SUCCESSFUL!")
    print("=" * 60)
    
    # Print summary
    courses = result.get('courses', [])
    print(f"\n📊 Extracted {len(courses)} courses total:")
    
    for i, course in enumerate(courses, 1):
        print(f"\n{i}. {course.get('course_code', 'N/A')}: {course.get('course_title', 'N/A')}")
        print(f"   Credits: {course.get('units', 'N/A')}")
        print(f"   Semester: {course.get('semester_taken', 'Not scheduled')}")
        print(f"   Section: {course.get('section', 'N/A')}")
        print(f"   Completed: {course.get('completed', False)}")
    
    # Print core/concentration breakdown
    print(f"\n📚 By Section:")
    print(f"   Core: {len(result.get('core_courses', []))}")
    print(f"   Concentration: {len(result.get('concentration_courses', []))}")
    print(f"   Elective: {len(result.get('elective_courses', []))}")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ EXTRACTION FAILED!")
    print("=" * 60)
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
