from app import db, app, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create a sample user
    user = User(username='test', password=generate_password_hash('test')) # type: ignore
    db.session.add(user)
    db.session.commit()
    print("Sample user created: test/test")
