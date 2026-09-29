import sys
import re
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import open_db

db = open_db()
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT id, email FROM users WHERE role='proctor'")
for row in cursor.fetchall():
    email = row['email']
    if ',' in email or ' ' in email:
        local_part, domain = email.split('@') if '@' in email else (email, '')
        
        # fix local part
        local_part = re.sub(r'[^a-z0-9]', '.', local_part.lower())
        local_part = re.sub(r'\.+', '.', local_part).strip('.')
        
        new_email = f"{local_part}@{domain}" if domain else local_part
        cursor.execute("UPDATE users SET email=%s WHERE id=%s", (new_email, row['id']))
        print(f"Fixed: {email} -> {new_email}")

db.commit()
print("Done fixing emails.")
