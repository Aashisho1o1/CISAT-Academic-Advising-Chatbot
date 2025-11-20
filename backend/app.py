import os
import json
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import LandingAI service
from landingai_service import LandingAIService

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_DOCS_DEST'] = 'uploads/'

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])  # Allow CORS for React frontend
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize LandingAI service
landingai_service = LandingAIService()

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='user')
    courses_taken = db.relationship('UserCourse', backref='user', lazy=True)
    advising_sheets = db.relationship('AdvisingSheet', backref='user', lazy=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    required = db.Column(db.Boolean, default=True)
    prerequisites = db.Column(db.Text)  # JSON list of course codes

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    grade = db.Column(db.String(5))

class AdvisingSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    parsed_data = db.Column(db.Text)  # JSON of parsed courses

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Helper function for request validation
def validate_json_request(required_fields):
    """Decorator to validate JSON requests have required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/api/login', methods=['POST'])
@validate_json_request(['username', 'password'])
def login():
    """
    User login endpoint
    Expects JSON: {"username": "...", "password": "..."}
    Returns: User data if successful, error if invalid credentials
    """
    data = request.get_json()
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    # Check if user exists and password is correct
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@app.route('/api/courses', methods=['GET', 'POST'])
@login_required
def courses():
    """
    GET: Returns all courses
    POST: Creates a new course
    Expects JSON: {"code": "...", "name": "...", "credits": int, "required": bool, "prerequisites": []}
    """
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['code', 'name', 'credits']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400
        
        # Create course
        try:
            prereqs = json.dumps(data.get('prerequisites', []))
            course = Course(
                code=data['code'],
                name=data['name'],
                credits=int(data['credits']),
                required=data.get('required', True),
                prerequisites=prereqs
            )
            db.session.add(course)
            db.session.commit()
            return jsonify({
                'message': 'Course added successfully',
                'course': {
                    'id': course.id,
                    'code': course.code,
                    'name': course.name
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        # GET: Return all courses
        all_courses = Course.query.all()
        return jsonify([{
            'id': c.id,
            'code': c.code,
            'name': c.name,
            'credits': c.credits,
            'required': c.required,
            'prerequisites': json.loads(c.prerequisites)
        } for c in all_courses]), 200

@app.route('/api/user/courses', methods=['GET', 'POST'])
@login_required
def user_courses():
    """
    GET: Returns all courses for the current user
    POST: Update or add a course for the current user
    """
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'course_code' not in data:
            return jsonify({'error': 'course_code is required'}), 400
        
        course = Course.query.filter_by(code=data['course_code']).first()
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        user_course = UserCourse.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        if user_course:
            # Update existing course
            user_course.completed = data.get('completed', False)
            user_course.grade = data.get('grade', '')
        else:
            # Add new course
            user_course = UserCourse(
                user_id=current_user.id,
                course_id=course.id,
                completed=data.get('completed', False),
                grade=data.get('grade', '')
            )
            db.session.add(user_course)
        
        db.session.commit()
        return jsonify({'message': 'Course updated successfully'}), 200
    else:
        # GET: Return all user courses - FIX N+1 QUERY PROBLEM
        user_courses_data = db.session.query(UserCourse, Course).join(
            Course, UserCourse.course_id == Course.id
        ).filter(UserCourse.user_id == current_user.id).all()
        
        result = [
            {
                'id': uc.id,
                'course': {
                    'code': course.code,
                    'name': course.name,
                    'credits': course.credits
                },
                'completed': uc.completed,
                'grade': uc.grade
            }
            for uc, course in user_courses_data
        ]
        return jsonify(result), 200

@app.route('/api/upload', methods=['POST'])
@login_required
def upload():
    """Upload advising sheet and extract course data using LandingAI"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(app.root_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    # Extract courses using LandingAI
    extracted_data = landingai_service.extract_courses(Path(filepath))
    
    # Save to database
    advising_sheet = AdvisingSheet(
        user_id=current_user.id,
        filename=filename,
        filepath=filepath,
        parsed_data=json.dumps(extracted_data)
    )
    db.session.add(advising_sheet)
    
    # Create courses and mark user courses
    courses_created = 0
    courses_updated = 0
    
    for course_data in extracted_data.get('courses', []):
        # Get or create course
        course = Course.query.filter_by(code=course_data['course_code']).first()
        if not course:
            course = Course(
                code=course_data['course_code'],
                name=course_data['course_name'],
                credits=course_data['credits'],
                required=True,
                prerequisites='[]'
            )
            db.session.add(course)
            db.session.flush()
            courses_created += 1
        
        # Get or create user course
        user_course = UserCourse.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        if not user_course:
            user_course = UserCourse(
                user_id=current_user.id,
                course_id=course.id,
                completed=course_data.get('completed', False),
                grade=course_data.get('grade', '')
            )
            db.session.add(user_course)
            courses_updated += 1
        else:
            user_course.completed = course_data.get('completed', False)
            user_course.grade = course_data.get('grade', '')
            courses_updated += 1
    
    db.session.commit()
    
    return jsonify({
        'message': 'File uploaded and courses extracted successfully',
        'id': advising_sheet.id,
        'extracted_data': extracted_data,
        'courses_created': courses_created,
        'courses_updated': courses_updated
    }), 200

@app.route('/api/upload/async', methods=['POST'])
@login_required
def upload_async():
    """
    Upload large file and create async extraction job
    For files > 50 pages, use this instead of regular upload
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Create async job
        job_id = landingai_service.extract_courses_async(Path(filepath))
        
        # Save advising sheet with job_id in parsed_data
        advising_sheet = AdvisingSheet(
            user_id=current_user.id,
            filename=filename,
            filepath=filepath,
            parsed_data=json.dumps({'job_id': job_id, 'status': 'processing'})
        )
        db.session.add(advising_sheet)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded, extraction in progress',
            'job_id': job_id,
            'advising_sheet_id': advising_sheet.id
        }), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/status/<job_id>', methods=['GET'])
@login_required
def upload_status(job_id: str):
    """
    Check status of async extraction job
    Returns: {status: 'processing'|'completed'|'failed', result: {...}}
    """
    try:
        status = landingai_service.get_job_status(job_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress')
@login_required
def progress():
    """
    Calculate graduation progress for current user
    Only counts required courses towards progress
    """
    # Total required courses in curriculum
    total_required = Course.query.filter_by(required=True).count()
    
    # Get completed course IDs for current user
    completed_course_ids = [
        uc.course_id for uc in UserCourse.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).all()
    ]
    
    # Count how many completed courses are required
    completed = Course.query.filter(
        Course.id.in_(completed_course_ids),
        Course.required == True
    ).count()
    
    # Calculate progress percentage
    progress_pct = (completed / total_required * 100) if total_required > 0 else 0
    
    return jsonify({
        'progress': round(progress_pct, 1),
        'completed': completed,
        'total': total_required
    }), 200

@app.route('/api/journey')
@login_required
def journey():
    """
    Generate journey map visualization data
    Returns nodes (courses) and edges (prerequisites) for graph visualization
    """
    # Get all courses
    courses = Course.query.all()
    
    # Get user's completed courses as a dictionary for fast lookup
    user_courses = {
        uc.course_id: uc.completed
        for uc in UserCourse.query.filter_by(user_id=current_user.id).all()
    }
    
    # Build nodes - each course is a node
    nodes = [
        {
            'id': c.code,
            'label': c.name,
            'completed': user_courses.get(c.id, False),
            'required': c.required,
            'credits': c.credits
        }
        for c in courses
    ]
    
    # Build edges - prerequisites create directed edges
    edges = []
    for c in courses:
        prereqs = json.loads(c.prerequisites) if c.prerequisites else []
        for prereq_code in prereqs:
            # Only add edge if prerequisite course exists
            if any(course.code == prereq_code for course in courses):
                edges.append({'from': prereq_code, 'to': c.code})
    
    return jsonify({'nodes': nodes, 'edges': edges}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)
