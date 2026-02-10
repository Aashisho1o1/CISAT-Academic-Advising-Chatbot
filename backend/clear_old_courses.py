"""One-time script to delete courses with HTML in their names"""
from app import app, db, Course, UserCourse

with app.app_context():
    # Find courses with HTML tags in the name
    bad_courses = Course.query.filter(
        db.or_(
            Course.name.like('%<%'),  # Contains < character
            Course.name.like('%>%'),  # Contains > character
            Course.code.like('%<%'),
            Course.code.like('%>%')
        )
    ).all()
    
    print(f"Found {len(bad_courses)} courses with HTML:")
    for course in bad_courses:
        print(f"  - {course.code}: {course.name[:50]}")
        
        # Delete user_course associations first
        UserCourse.query.filter_by(course_id=course.id).delete()
        
        # Delete the course
        db.session.delete(course)
    
    db.session.commit()
    print(f"✅ Deleted {len(bad_courses)} bad courses")
    
    # Show remaining courses
    remaining = Course.query.all()
    print(f"\n✅ Remaining clean courses: {len(remaining)}")
    for course in remaining:
        print(f"  - {course.code}: {course.name}")
