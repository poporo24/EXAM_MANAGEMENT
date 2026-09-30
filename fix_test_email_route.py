import re
app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'@app\.route\("/settings/test_email", methods=\["POST"\]\)\ndef test_email\(\):.*?return redirect\(url_for\(\'settings_page\'\)\)', re.DOTALL)

new_route = '''@app.route("/settings/test_email", methods=["POST"])
def test_email():
    guard = require_role('admin')
    if guard: return guard
    to = request.form.get("test_to", "")
    if not to:
        flash("Enter a recipient email address.", "warning")
        return redirect(url_for('settings_page'))
    try:
        # Instead of hanging the server with Flask-Mail, let's manually test the connection with a 5-second timeout
        import smtplib
        import socket
        s = get_system_settings()
        host = s.get('smtp_host', '')
        port = int(s.get('smtp_port') or 587)
        user = s.get('smtp_user', '')
        password = s.get('smtp_password', '')
        use_tls = bool(s.get('smtp_use_tls', 1))
        
        # Test TCP connection first
        try:
            socket.create_connection((host, port), timeout=5)
        except Exception as e:
            flash(f"Connection blocked or timed out (Port {port} might be blocked by Render Free Tier): {e}", "danger")
            return redirect(url_for('settings_page'))
            
        # Try full SMTP handshake
        server = smtplib.SMTP(host, port, timeout=5)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(user, password)
        
        # If we reach here, connection works! Send the email.
        msg = f"Subject: CCA Exam Management - Test Email\\n\\nThis is a test email. SMTP works!"
        server.sendmail(user, [to], msg)
        server.quit()
        
        flash(f"Test email successfully sent to {to}!", "success")
    except smtplib.SMTPAuthenticationError:
        flash("SMTP Authentication Failed. Check your App Password.", "danger")
    except Exception as e:
        flash(f"SMTP Error: {e}", "danger")
        
    return redirect(url_for('settings_page'))'''

match = pattern.search(content)
if match:
    content = content.replace(match.group(0), new_route)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed test_email route with timeout and detailed errors!")
else:
    print("Could not find test_email route!")
