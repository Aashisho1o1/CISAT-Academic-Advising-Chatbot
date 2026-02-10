"""Manual script to inspect LandingAI parse response structure."""

import os
from pathlib import Path

from dotenv import load_dotenv
from landingai_ade import LandingAIADE


def run_parse_debug() -> None:
  load_dotenv()

  api_key = os.environ.get('VISION_AGENT_API_KEY')
  if not api_key:
    raise RuntimeError('VISION_AGENT_API_KEY not set in .env')

  client = LandingAIADE(apikey=api_key)
  test_file = Path('uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf')

  if not test_file.exists():
    print(f'File not found: {test_file}')
    return

  print(f'Testing with: {test_file} ({test_file.stat().st_size} bytes)')

  try:
    print('\nCalling LandingAI parse API...')
    response = client.parse(document=test_file, model='dpt-2-latest')

    print('Parse succeeded')
    print(f'Response type: {type(response)}')
    print(f'Response attributes: {dir(response)}')

  except Exception as exc:
    print(f'Parse failed: {exc}')


if __name__ == '__main__':
  run_parse_debug()
