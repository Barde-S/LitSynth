# email_service.py
# Email service for sending OTP codes

import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Email Configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'noreply@litsynth.com')

DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))


def get_otp_expiry() -> datetime:
    """Get the expiry time for an OTP (10 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)


def send_otp_email(to_email: str, otp_code: str, purpose: str = "registration") -> bool:
    """
    Send OTP email to user

    Args:
        to_email: Recipient email address
        otp_code: The OTP code to send
        purpose: 'registration' or 'password_reset'

    Returns:
        True if email sent successfully, False otherwise
    """

    # In debug mode without SMTP config, just log and return True
    if DEBUG and not SMTP_USER:
        print(f"[EMAIL DEBUG] Would send OTP to {to_email}: {otp_code}")
        return True

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[EMAIL ERROR] SMTP credentials not configured")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"LitSynth - Your Verification Code: {otp_code}"
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = to_email

        # Email content based on purpose
        if purpose == "registration":
            subject_text = "Email Verification"
            action_text = "complete your registration"
        else:
            subject_text = "Password Reset"
            action_text = "reset your password"

        # Plain text version
        text_content = f"""
LitSynth - {subject_text}

Your verification code is: {otp_code}

Use this code to {action_text}. This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you didn't request this code, please ignore this email.

- The LitSynth Team
        """

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #667eea; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LitSynth</h1>
            <p>{subject_text}</p>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Your verification code is:</p>
            <div class="otp-code">{otp_code}</div>
            <p>Use this code to {action_text}. This code will expire in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 LitSynth - Academic Research Assistant</p>
        </div>
    </div>
</body>
</html>
        """

        # Attach both versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())

        if DEBUG:
            print(f"[EMAIL] OTP sent successfully to {to_email}")

        return True

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")
        return False
