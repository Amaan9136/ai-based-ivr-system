import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient_email: str, message: str, title: str = 'Notes from SAAS IVR System') -> bool:
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')

    if not sender_email or not sender_password:
        raise ValueError("Email credentials not set in environment variables.")

    if not recipient_email or not message:
        raise ValueError("Recipient email and message are required.")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = title
    msg.attach(MIMEText(message, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"✅ Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
