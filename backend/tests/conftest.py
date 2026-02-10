import json
import os

import pytest
from werkzeug.security import generate_password_hash

os.environ['SECRET_KEY'] = 'pytest-secret-key'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pytest_advising.db'
os.environ['VISION_AGENT_API_KEY'] = 'test-api-key'
os.environ['RATELIMIT_STORAGE_URI'] = 'memory://'
os.environ['FLASK_DEBUG'] = 'false'

from app import AdvisingSheet, Course, User, app, db  # noqa: E402


@pytest.fixture(scope='session')
def flask_app():
  app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

  if 'test_error' not in app.view_functions:
    @app.route('/api/test-error', methods=['GET'])
    def test_error():
      raise RuntimeError('forced server error')

  return app


@pytest.fixture(autouse=True)
def seed_database(flask_app):
  with flask_app.app_context():
    db.drop_all()
    db.create_all()

    student = User(
      username='student',
      password=generate_password_hash('student-pass'),
      role='user',
    )
    admin = User(
      username='admin',
      password=generate_password_hash('admin-pass'),
      role='admin',
    )
    other = User(
      username='other',
      password=generate_password_hash('other-pass'),
      role='user',
    )
    db.session.add_all([student, admin, other])
    db.session.flush()

    course = Course(
      code='IST 101',
      name='Intro to IST',
      credits=4,
      required=True,
      prerequisites='[]',
    )
    db.session.add(course)

    user_job = AdvisingSheet(
      user_id=student.id,
      filename='student.csv',
      filepath='uploads/student.csv',
      parsed_data=json.dumps({'job_id': 'job-student', 'status': 'processing'}),
    )
    other_job = AdvisingSheet(
      user_id=other.id,
      filename='other.csv',
      filepath='uploads/other.csv',
      parsed_data=json.dumps({'job_id': 'job-other', 'status': 'processing'}),
    )
    db.session.add_all([user_job, other_job])
    db.session.commit()

  yield

  with flask_app.app_context():
    db.session.remove()


@pytest.fixture
def client(flask_app):
  return flask_app.test_client()
