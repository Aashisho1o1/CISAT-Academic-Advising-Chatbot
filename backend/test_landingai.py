"""
Test script for LandingAI integration
Run this to verify the extraction works before testing in the web app
"""
import json
from pathlib import Path
from landingai_service import LandingAIService

def test_extraction():
    print("=" * 60)
    print("TESTING LANDINGAI EXTRACTION")
    print("=" * 60)
    
    # Initialize service
    service = LandingAIService()
    print("✓ LandingAI service initialized")
    
    # Test file path
    test_file = Path("uploads/sample_advising_sheet.txt")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        print("Please create the sample file first.")
        return
    
    print(f"✓ Test file found: {test_file}")
    print(f"  File size: {test_file.stat().st_size} bytes")
    print()
    
    # Extract courses
    print("🚀 Starting extraction...")
    print("-" * 60)
    
    try:
        result = service.extract_courses(test_file)
        
        print("✅ EXTRACTION SUCCESSFUL!")
        print()
        print("📊 RESULTS:")
        print("-" * 60)
        print(json.dumps(result, indent=2))
        print("-" * 60)
        print()
        
        # Summary
        if 'courses' in result:
            print(f"📚 Total Courses Extracted: {len(result['courses'])}")
            completed = sum(1 for c in result['courses'] if c.get('completed', False))
            print(f"✅ Completed: {completed}")
            print(f"⏳ In Progress/Pending: {len(result['courses']) - completed}")
        
        if result.get('student_name'):
            print(f"👤 Student: {result['student_name']}")
        if result.get('program'):
            print(f"🎓 Program: {result['program']}")
        
        print()
        print("=" * 60)
        print("TEST PASSED! You can now use the web app.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ EXTRACTION FAILED!")
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check your VISION_AGENT_API_KEY in .env file")
        print("2. Ensure landingai-ade package is installed")
        print("3. Verify your LandingAI account has credits")
        print("4. Check the sample file format")

if __name__ == "__main__":
    test_extraction()
