import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from system.database import get_system_settings

def send_reset_email(to_email, reset_link):
    settings = get_system_settings()
    host = settings.get('smtp_host')
    port = settings.get('smtp_port', 587)
    user = settings.get('smtp_user')
    password = settings.get('smtp_password')
    from_addr = settings.get('smtp_from') or user
    use_tls = settings.get('smtp_use_tls', 1)

    # If SMTP is missing, just return False but print link for testing!
    if not all([host, user, password]):
        print(f"\n{'='*50}\nDEBUG MOCK EMAIL:\nTo: {to_email}\nReset Link: {reset_link}\n{'='*50}\n")
        return False, "SMTP server not configured."

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_email
    msg['Subject'] = "CCA Exams - Password Reset Request"

    body = f"""Hello,
    
We received a request to reset your password. Please click the link below to set a new password:

{reset_link}

If you did not request this, please ignore this email. Your password will remain unchanged.

Regards,
CCA Exam Management System"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(host, int(port))
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
