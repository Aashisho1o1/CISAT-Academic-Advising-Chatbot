import io

from app import app, landingai_service


def login(client, username: str, password: str, remote_addr: str = '127.0.0.1'):
  return client.post(
    '/api/login',
    json={'username': username, 'password': password},
    environ_base={'REMOTE_ADDR': remote_addr},
  )


def test_logout_invalidates_session_and_me_requires_auth(client):
  login_response = login(client, 'student', 'student-pass')
  assert login_response.status_code == 200

  me_response = client.get('/api/me')
  assert me_response.status_code == 200
  assert me_response.get_json()['user']['username'] == 'student'

  logout_response = client.post('/api/logout')
  assert logout_response.status_code == 200

  me_after_logout = client.get('/api/me')
  assert me_after_logout.status_code == 401


def test_login_rate_limit_returns_429_after_five_attempts(client):
  remote_addr = '10.10.10.10'
  for _ in range(5):
    response = login(client, 'student', 'wrong-password', remote_addr=remote_addr)
    assert response.status_code == 401

  blocked_response = login(client, 'student', 'wrong-password', remote_addr=remote_addr)
  assert blocked_response.status_code == 429


def test_non_admin_cannot_create_course(client):
  assert login(client, 'student', 'student-pass').status_code == 200

  response = client.post(
    '/api/courses',
    json={
      'code': 'IST 999',
      'name': 'Privileged Course',
      'credits': 4,
      'required': True,
      'prerequisites': [],
    },
  )

  assert response.status_code == 403
  assert response.get_json()['error'] == 'Admin access required'


def test_upload_validation_rejects_missing_invalid_and_oversized_files(client):
  assert login(client, 'student', 'student-pass').status_code == 200

  missing_response = client.post('/api/upload', data={}, content_type='multipart/form-data')
  assert missing_response.status_code == 400

  invalid_type_response = client.post(
    '/api/upload',
    data={'file': (io.BytesIO(b'bad'), 'malware.exe')},
    content_type='multipart/form-data',
  )
  assert invalid_type_response.status_code == 400

  original_limit = app.config['MAX_CONTENT_LENGTH']
  app.config['MAX_CONTENT_LENGTH'] = 10

  try:
    oversized_response = client.post(
      '/api/upload',
      data={'file': (io.BytesIO(b'01234567890'), 'valid.pdf')},
      content_type='multipart/form-data',
    )
  finally:
    app.config['MAX_CONTENT_LENGTH'] = original_limit

  assert oversized_response.status_code == 413


def test_upload_status_requires_job_ownership(client, monkeypatch):
  assert login(client, 'student', 'student-pass').status_code == 200

  monkeypatch.setattr(
    landingai_service,
    'get_job_status',
    lambda job_id: {'job_id': job_id, 'status': 'processing', 'result': None},
  )

  own_job_response = client.get('/api/upload/status/job-student')
  assert own_job_response.status_code == 200

  other_job_response = client.get('/api/upload/status/job-other')
  assert other_job_response.status_code == 404


def test_json_error_handlers_for_404_and_500(client):
  missing_response = client.get('/api/no-such-route')
  assert missing_response.status_code == 404
  assert missing_response.is_json
  assert missing_response.get_json()['error'] == 'Resource not found'

  error_response = client.get('/api/test-error')
  assert error_response.status_code == 500
  assert error_response.is_json
  assert error_response.get_json()['error'] == 'Internal server error'
