"""Manual script for testing extraction with a real PDF."""

from pathlib import Path

from dotenv import load_dotenv

from landingai_service import LandingAIService


def run_real_pdf_test() -> None:
  load_dotenv()

  service = LandingAIService()
  test_file = Path('uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf')

  print('=' * 60)
  print('TESTING WITH ACTUAL PDF')
  print('=' * 60)

  if not test_file.exists():
    print(f'File not found: {test_file}')
    return

  print(f'File: {test_file}')
  print(f'Size: {test_file.stat().st_size} bytes')
  print()

  try:
    print('Starting extraction...')
    print('-' * 60)

    result = service.extract_courses(test_file)

    print('\n' + '=' * 60)
    print('EXTRACTION SUCCESSFUL')
    print('=' * 60)

    courses = result.get('courses', [])
    print(f'\nExtracted {len(courses)} courses total:')

    for i, course in enumerate(courses, 1):
      print(f"\n{i}. {course.get('course_code', 'N/A')}: {course.get('course_title', 'N/A')}")
      print(f"   Credits: {course.get('units', 'N/A')}")
      print(f"   Semester: {course.get('semester_taken', 'Not scheduled')}")
      print(f"   Section: {course.get('section', 'N/A')}")
      print(f"   Completed: {course.get('completed', False)}")

  except Exception as exc:
    print('\n' + '=' * 60)
    print('EXTRACTION FAILED')
    print('=' * 60)
    print(f'Error: {exc}')


if __name__ == '__main__':
  run_real_pdf_test()
