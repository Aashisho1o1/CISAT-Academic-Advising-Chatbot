import json
import logging
import os
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from landingai_service import LandingAIService

try:
    from flask_limiter import Limiter # type: ignore
    from flask_limiter.util import get_remote_address
    FLASK_LIMITER_AVAILABLE = True
except ImportError:
    FLASK_LIMITER_AVAILABLE = False

    class Limiter:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

        def limit(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    def get_remote_address() -> str:
        return request.remote_addr or "127.0.0.1"

try:
    from flask_migrate import Migrate # type: ignore
except ImportError:
    class Migrate:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DEFAULT_MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "xlsx", "xls", "csv"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/csv",
    "application/octet-stream",
}
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW_SECONDS = 60
_fallback_login_attempts: dict[str, list[float]] = {}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///advising.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED_DOCS_DEST"] = "uploads/"
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("MAX_CONTENT_LENGTH", str(DEFAULT_MAX_CONTENT_LENGTH))
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
CORS(app, supports_credentials=True, origins=cors_origins)

if os.getenv("SECRET_KEY") in {None, "", "your-secret-key-here-change-this"}:
    logger.warning("Using weak or placeholder SECRET_KEY. Set a strong key in .env.")

if app.config["MAX_CONTENT_LENGTH"] <= 0:
    logger.warning("Invalid MAX_CONTENT_LENGTH configured. Falling back to 16MB.")
    app.config["MAX_CONTENT_LENGTH"] = DEFAULT_MAX_CONTENT_LENGTH

db = SQLAlchemy(app)
migrate = Migrate(app, db)
if Migrate.__module__ == __name__:
    logger.warning("Flask-Migrate is not installed. Migration commands will be unavailable.")

login_manager = LoginManager(app)
login_manager.login_view = "login"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)

if not FLASK_LIMITER_AVAILABLE:
    logger.warning(
        "Flask-Limiter is not installed. Falling back to in-memory login throttling."
    )

landingai_service = LandingAIService()


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="user")
    courses_taken = db.relationship("UserCourse", backref="user", lazy=True)
    advising_sheets = db.relationship("AdvisingSheet", backref="user", lazy=True)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    required = db.Column(db.Boolean, default=True)
    prerequisites = db.Column(db.Text)


class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    grade = db.Column(db.String(5))
    semester_taken = db.Column(db.String(20))


class AdvisingSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    parsed_data = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized() -> tuple[dict[str, str], int]:
    return jsonify({"error": "Authentication required"}), 401


@app.errorhandler(404)
def not_found(_error: Any) -> tuple[dict[str, str], int]:
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(_error: Any) -> tuple[dict[str, str], int]:
    max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    return jsonify({"error": f"File too large. Maximum allowed size is {max_mb}MB"}), 413


@app.errorhandler(500)
def internal_server_error(error: Any) -> tuple[dict[str, str], int]:
    logger.exception("Unhandled server error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


# Helper functions

def validate_json_request(required_fields: list[str]):
    """Decorator to validate JSON requests have required fields."""

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return (
                    jsonify({
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }),
                    400,
                )

            return func(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(func):
    """Decorator to enforce admin-only access."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs)

    return decorated_function


def parse_json_text(value: Optional[str]) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def get_prerequisites(prereq_text: Optional[str]) -> list[str]:
    if not prereq_text:
        return []
    try:
        parsed = json.loads(prereq_text)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def is_allowed_upload(filename: str, mimetype: Optional[str]) -> bool:
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False

    if mimetype and mimetype not in ALLOWED_MIME_TYPES:
        return False

    return True


def user_owns_job_id(user_id: int, job_id: str) -> bool:
    user_sheets = AdvisingSheet.query.filter_by(user_id=user_id).all()
    for sheet in user_sheets:
        parsed = parse_json_text(sheet.parsed_data)
        if parsed.get("job_id") == job_id:
            return True
    return False


def is_rate_limited(remote_addr: str) -> bool:
    """Fallback in-memory login limiter when Flask-Limiter is unavailable."""
    now = time.time()
    attempts = _fallback_login_attempts.get(remote_addr, [])
    valid_attempts = [attempt for attempt in attempts if now - attempt < LOGIN_RATE_WINDOW_SECONDS]
    _fallback_login_attempts[remote_addr] = valid_attempts

    if len(valid_attempts) >= LOGIN_RATE_LIMIT:
        return True

    valid_attempts.append(now)
    _fallback_login_attempts[remote_addr] = valid_attempts
    return False


# Routes
@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
@validate_json_request(["username", "password"])
def login():
    """Authenticate user and establish session."""
    data = request.get_json(silent=True) or {}
    remote_addr = request.remote_addr or "127.0.0.1"

    if not FLASK_LIMITER_AVAILABLE and is_rate_limited(remote_addr):
        return jsonify({"error": "Too many login attempts. Please try again later."}), 429

    user = User.query.filter_by(username=data["username"]).first()
    if user and check_password_hash(user.password, data["password"]):
        _fallback_login_attempts.pop(remote_addr, None)
        login_user(user)
        return (
            jsonify(
                {
                    "message": "Logged in successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role,
                    },
                }
            ),
            200,
        )

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/me", methods=["GET"])
@login_required
def me():
    return (
        jsonify(
            {
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "role": current_user.role,
                }
            }
        ),
        200,
    )


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@app.route("/api/courses", methods=["GET", "POST"])
@login_required
def courses():
    """GET all courses or POST a new course (admin only)."""
    if request.method == "POST":
        return create_course()

    all_courses = Course.query.all()
    return (
        jsonify(
            [
                {
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "credits": c.credits,
                    "required": c.required,
                    "prerequisites": get_prerequisites(c.prerequisites),
                }
                for c in all_courses
            ]
        ),
        200,
    )


@admin_required
def create_course():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["code", "name", "credits"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        course = Course(
            code=data["code"],
            name=data["name"],
            credits=int(data["credits"]),
            required=data.get("required", True),
            prerequisites=json.dumps(data.get("prerequisites", [])),
        )
        db.session.add(course)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Course added successfully",
                    "course": {
                        "id": course.id,
                        "code": course.code,
                        "name": course.name,
                    },
                }
            ),
            201,
        )
    except Exception as exc:
        db.session.rollback()
        logger.exception("Failed to create course: %s", exc)
        return jsonify({"error": "Failed to create course"}), 400


@app.route("/api/user/courses", methods=["GET", "POST"])
@login_required
def user_courses():
    """GET or upsert user course records."""
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data or "course_code" not in data:
            return jsonify({"error": "course_code is required"}), 400

        course = Course.query.filter_by(code=data["course_code"]).first()
        if not course:
            return jsonify({"error": "Course not found"}), 404

        user_course = UserCourse.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
        ).first()

        if user_course:
            user_course.completed = data.get("completed", False)
            user_course.grade = data.get("grade", "")
            user_course.semester_taken = data.get("semester_taken")
        else:
            user_course = UserCourse(
                user_id=current_user.id,
                course_id=course.id,
                completed=data.get("completed", False),
                grade=data.get("grade", ""),
                semester_taken=data.get("semester_taken"),
            )
            db.session.add(user_course)

        db.session.commit()
        return jsonify({"message": "Course updated successfully"}), 200

    user_courses_data = (
        db.session.query(UserCourse, Course)
        .join(Course, UserCourse.course_id == Course.id)
        .filter(UserCourse.user_id == current_user.id)
        .all()
    )

    result = [
        {
            "id": uc.id,
            "course": {
                "code": course.code,
                "name": course.name,
                "credits": course.credits,
            },
            "completed": uc.completed,
            "grade": uc.grade,
            "semester_taken": uc.semester_taken,
        }
        for uc, course in user_courses_data
    ]
    return jsonify(result), 200


@app.route("/api/upload", methods=["POST"])
@login_required
def upload():
    """Upload advising sheet and extract course data using LandingAI."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    if not is_allowed_upload(filename, file.mimetype):
        return (
            jsonify(
                {
                    "error": "Invalid file type. Allowed: PDF, XLSX, XLS, CSV"
                }
            ),
            400,
        )

    try:
        upload_dir = os.path.join(app.root_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        extracted_data = landingai_service.extract_courses(Path(filepath))

        advising_sheet = AdvisingSheet(
            user_id=current_user.id,
            filename=filename,
            filepath=filepath,
            parsed_data=json.dumps(extracted_data),
        )
        db.session.add(advising_sheet)

        courses_created = 0
        courses_updated = 0

        for course_data in extracted_data.get("courses", []):
            course_code = course_data.get("course_code")
            if not course_code:
                continue

            course = Course.query.filter_by(code=course_code).first()
            if not course:
                course = Course(
                    code=course_code,
                    name=course_data.get("course_name")
                    or course_data.get("course_title", "Unknown Course"),
                    credits=int(course_data.get("credits", 0)),
                    required=True,
                    prerequisites="[]",
                )
                db.session.add(course)
                db.session.flush()
                courses_created += 1

            user_course = UserCourse.query.filter_by(
                user_id=current_user.id,
                course_id=course.id,
            ).first()

            if not user_course:
                user_course = UserCourse(
                    user_id=current_user.id,
                    course_id=course.id,
                    completed=course_data.get("completed", False),
                    grade=course_data.get("grade", ""),
                    semester_taken=course_data.get("semester_taken"),
                )
                db.session.add(user_course)
            else:
                user_course.completed = course_data.get("completed", False)
                user_course.grade = course_data.get("grade", "")
                user_course.semester_taken = course_data.get("semester_taken")
            courses_updated += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "File uploaded and courses extracted successfully",
                    "id": advising_sheet.id,
                    "extracted_data": extracted_data,
                    "courses_created": courses_created,
                    "courses_updated": courses_updated,
                }
            ),
            200,
        )
    except Exception as exc:
        db.session.rollback()
        logger.exception("Upload processing failed: %s", exc)
        return jsonify({"error": "Failed to process uploaded file"}), 500


@app.route("/api/upload/async", methods=["POST"])
@login_required
def upload_async():
    """Upload file and create async extraction job."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    if not is_allowed_upload(filename, file.mimetype):
        return (
            jsonify(
                {
                    "error": "Invalid file type. Allowed: PDF, XLSX, XLS, CSV"
                }
            ),
            400,
        )

    try:
        upload_dir = os.path.join(app.root_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        job_id = landingai_service.extract_courses_async(Path(filepath))

        advising_sheet = AdvisingSheet(
            user_id=current_user.id,
            filename=filename,
            filepath=filepath,
            parsed_data=json.dumps({"job_id": job_id, "status": "processing"}),
        )
        db.session.add(advising_sheet)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "File uploaded, extraction in progress",
                    "job_id": job_id,
                    "advising_sheet_id": advising_sheet.id,
                }
            ),
            202,
        )
    except Exception as exc:
        db.session.rollback()
        logger.exception("Failed to create async extraction job: %s", exc)
        return jsonify({"error": "Failed to create extraction job"}), 500


@app.route("/api/upload/status/<job_id>", methods=["GET"])
@login_required
def upload_status(job_id: str):
    """Check async extraction status for a job owned by current user."""
    if not user_owns_job_id(current_user.id, job_id):
        return jsonify({"error": "Job not found"}), 404

    try:
        status = landingai_service.get_job_status(job_id)
        return jsonify(status), 200
    except Exception as exc:
        logger.exception("Failed to get upload status for %s: %s", job_id, exc)
        return jsonify({"error": "Failed to fetch upload status"}), 500


@app.route("/api/progress", methods=["GET"])
@login_required
def progress():
    """Calculate graduation progress for current user."""
    total_required = Course.query.filter_by(required=True).count()

    completed_course_ids = [
        uc.course_id
        for uc in UserCourse.query.filter_by(
            user_id=current_user.id,
            completed=True,
        ).all()
    ]

    completed = 0
    if completed_course_ids:
        completed = Course.query.filter(
            Course.id.in_(completed_course_ids),
            Course.required.is_(True),
        ).count()

    progress_pct = (completed / total_required * 100) if total_required > 0 else 0

    return (
        jsonify(
            {
                "progress": round(progress_pct, 1),
                "completed": completed,
                "total": total_required,
            }
        ),
        200,
    )


@app.route("/api/journey", methods=["GET"])
@login_required
def journey():
    """Generate journey map visualization data."""
    courses = Course.query.all()

    user_courses_map = {
        uc.course_id: uc for uc in UserCourse.query.filter_by(user_id=current_user.id).all()
    }

    nodes = []
    for course in courses:
        user_course = user_courses_map.get(course.id)
        nodes.append(
            {
                "id": course.code,
                "label": course.name,
                "completed": user_course.completed if user_course else False,
                "required": course.required,
                "credits": course.credits,
                "semester": user_course.semester_taken if user_course else None,
            }
        )

    all_codes = {course.code for course in courses}
    edges = []
    for course in courses:
        prereqs = get_prerequisites(course.prerequisites)
        for prereq_code in prereqs:
            if prereq_code in all_codes:
                edges.append({"from": prereq_code, "to": course.code})

    return jsonify({"nodes": nodes, "edges": edges}), 200


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=int(os.getenv("PORT", "8000")))
