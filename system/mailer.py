import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from system.database import get_system_settings

def send_via_brevo(api_key, to_email, subject, body, sender_email=None, sender_name=None):
    """Send an email using Brevo's HTTPS API (Port 443) which bypasses all cloud SMTP blocks."""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {
            "name": sender_name or "CCA Exam Management System",
            "email": sender_email or "jpbaltazar23-0368@cca.edu.ph"
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201, 202):
            return True, "Email sent successfully via Brevo API."
        return False, f"Brevo Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Brevo request failed: {e}"

def send_reset_email(to_email, reset_link):
    settings = get_system_settings()
    host = settings.get('smtp_host')
    port = settings.get('smtp_port', 587)
    user = settings.get('smtp_user')
    password = (settings.get('smtp_password') or '').replace(' ', '').strip()
    from_addr = settings.get('smtp_from') or user
    use_tls = settings.get('smtp_use_tls', 1)

    brevo_key = os.environ.get('BREVO_API_KEY') or settings.get('brevo_api_key')
    if not brevo_key and password and password.startswith('xkeysib-'):
        brevo_key = password

    subject = "CCA Exams - Password Reset Request"
    body = f"""Hello,
    
We received a request to reset your password. Please click the link below to set a new password:

{reset_link}

If you did not request this, please ignore this email. Your password will remain unchanged.

Regards,
CCA Exam Management System"""

    # If Brevo API key is available, send via HTTPS Port 443!
    if brevo_key:
        ok, msg = send_via_brevo(brevo_key, to_email, subject, body, sender_email=from_addr or user)
        if ok:
            return True, msg
        print(f"[Brevo Fallback Warning] {msg}")

    # Standard SMTP Fallback
    if not all([host, user, password]):
        print(f"\n{'='*50}\nDEBUG MOCK EMAIL:\nTo: {to_email}\nReset Link: {reset_link}\n{'='*50}\n")
        return False, "SMTP server not configured."

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        if int(port) == 465:
            server = smtplib.SMTP_SSL(host, int(port), timeout=10)
        else:
            server = smtplib.SMTP(host, int(port), timeout=10)
            if use_tls:
                server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully."
    except Exception as e:
        print(f"Email error: {e}")
        print(f"\n{'='*50}\nDEBUG MOCK EMAIL:\nTo: {to_email}\nReset Link: {reset_link}\n{'='*50}\n")
        return False, str(e)

