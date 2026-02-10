"""Test upload endpoint with curl simulation"""
import requests

# Login first
login_response = requests.post(
    'http://127.0.0.1:8000/api/login',
    json={'username': 'demo', 'password': 'demo123'}
)

if login_response.status_code == 200:
    print("✅ Logged in successfully")
    session_cookie = login_response.cookies
    
    # Upload PDF
    with open('uploads/Aashish_Academic_Planning_Sheet_MS.docx.pdf', 'rb') as f:
        files = {'file': f}
        upload_response = requests.post(
            'http://127.0.0.1:8000/api/upload',
            files=files,
            cookies=session_cookie
        )
    
    print(f"\nUpload status code: {upload_response.status_code}")
    print(f"Upload response:\n{upload_response.json()}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
