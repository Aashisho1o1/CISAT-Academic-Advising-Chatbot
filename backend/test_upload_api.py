"""Manual script to test upload endpoint with requests (not run by pytest)."""

import requests


def run_upload_api_test() -> None:
  login_response = requests.post(
    'http://127.0.0.1:8000/api/login',
    json={'username': 'demo', 'password': 'demo123'},
    timeout=20,
  )

  if login_response.status_code != 200:
    print(f'Login failed: {login_response.status_code}')
    print(f'Response: {login_response.text}')
    return

  print('Logged in successfully')

  with open('uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf', 'rb') as file_handle:
    files = {'file': file_handle}
    upload_response = requests.post(
      'http://127.0.0.1:8000/api/upload',
      files=files,
      cookies=login_response.cookies,
      timeout=60,
    )

  print(f'Upload status code: {upload_response.status_code}')
  print(f'Upload response: {upload_response.text}')


if __name__ == '__main__':
  run_upload_api_test()
