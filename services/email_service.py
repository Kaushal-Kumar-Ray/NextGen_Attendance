import requests
import os

def send_email_otp(to_email, otp):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": "NextGen Attendance",
            "email": "raykaushal456@gmail.com"   # can be same gmail initially
        },
        "to": [
            {"email": to_email}
        ],
        "subject": "Your Admin Login OTP",
        "htmlContent": f"""
        <h2>🔐 Admin Login OTP</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP is valid for 5 minutes.</p>
        """
    }

    response = requests.post(url, headers=headers, json=data)

    return response.status_code == 201