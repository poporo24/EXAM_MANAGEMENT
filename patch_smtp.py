import os
import re

# Patch app.py
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

old_tcp_msg = 'flash(f"Connection blocked or timed out (Port {port} might be blocked by Render Free Tier): {e}", "danger")'
new_tcp_msg = 'flash(f"Connection blocked or timed out (Port {port} might be blocked by your ISP or firewall): {e}", "danger")'
app_code = app_code.replace(old_tcp_msg, new_tcp_msg)

old_smtp_handshake = '''        # Try full SMTP handshake
        server = smtplib.SMTP(host, port, timeout=5)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(user, password)'''

new_smtp_handshake = '''        # Try full SMTP handshake
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=5)
            server.ehlo()
        else:
            server = smtplib.SMTP(host, port, timeout=5)
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
        server.login(user, password)'''

app_code = app_code.replace(old_smtp_handshake, new_smtp_handshake)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# Patch system/mailer.py
with open("system/mailer.py", "r", encoding="utf-8") as f:
    mailer_code = f.read()

old_mailer = '''    try:
        server = smtplib.SMTP(host, int(port))
        if use_tls:
            server.starttls()
        server.login(user, password)'''

new_mailer = '''    try:
        if int(port) == 465:
            server = smtplib.SMTP_SSL(host, int(port))
        else:
            server = smtplib.SMTP(host, int(port))
            if use_tls:
                server.starttls()
        server.login(user, password)'''

mailer_code = mailer_code.replace(old_mailer, new_mailer)

with open("system/mailer.py", "w", encoding="utf-8") as f:
    f.write(mailer_code)

print("Patched.")
