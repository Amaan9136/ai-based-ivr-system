import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, request, jsonify

email_routes = Blueprint('email_routes', __name__, url_prefix='/email')

def send_email(sender_email, sender_password, recipient_email, message, title):
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
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise e

@email_routes.route('/send-mail', methods=['POST'])
def send_mail():
    data = request.get_json()
    title = data.get('title', 'Notes from SAAS IVR System')
    message = data.get('message')
    recipient_email = data.get('recipient_email')

    if not recipient_email or not message:
        return jsonify({'status': 'error', 'message': 'Missing recipient email or message'}), 400

    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')

    if not sender_email or not sender_password:
        return jsonify({'status': 'error', 'message': 'Email credentials not set in environment'}), 500

    try:
        send_email(sender_email, sender_password, recipient_email, message, title)
        return jsonify({'status': 'success', 'message': 'Email sent successfully!'})
    except Exception:
        return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500
