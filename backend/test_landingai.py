"""Manual script for LandingAI extraction checks (not part of pytest suite)."""

import json
from pathlib import Path

from landingai_service import LandingAIService


def run_extraction() -> None:
  print('=' * 60)
  print('TESTING LANDINGAI EXTRACTION')
  print('=' * 60)

  service = LandingAIService()
  print('LandingAI service initialized')

  test_file = Path('uploads/sample_advising_sheet.txt')

  if not test_file.exists():
    print(f'Test file not found: {test_file}')
    return

  print(f'Test file found: {test_file}')
  print(f'File size: {test_file.stat().st_size} bytes')
  print()

  print('Starting extraction...')
  print('-' * 60)

  try:
    result = service.extract_courses(test_file)

    print('EXTRACTION SUCCESSFUL')
    print(json.dumps(result, indent=2))

  except Exception as exc:
    print(f'EXTRACTION FAILED: {exc}')


if __name__ == '__main__':
  run_extraction()
