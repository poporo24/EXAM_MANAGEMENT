"""
seed_secretaries.py
Creates one secretary account per institute, scoped by institute_id.
Run: python seed_secretaries.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import bcrypt
from system.database import open_db

db = open_db()
if not db:
    print("ERROR: Cannot connect to MySQL.")
    sys.exit(1)

c = db.cursor()

# Remove old generic secretary (no institute)
c.execute("DELETE FROM users WHERE email='secretary@cca.edu.ph'")
print(f"Removed old generic secretary: {c.rowcount} row(s)")

# Per-institute secretary accounts
secretaries = [
    ('IEAS Secretary',   'secretary.ieas@cca.edu.ph',   'secretary123', 'secretary', 1),
    ('IBM Secretary',    'secretary.ibm@cca.edu.ph',    'secretary123', 'secretary', 2),
    ('ICSLIS Secretary', 'secretary.icslis@cca.edu.ph', 'secretary123', 'secretary', 3),
]

for full_name, email, pwd, role, inst_id in secretaries:
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
    c.execute("SELECT id FROM users WHERE email=%s", (email,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (full_name, email, password, role, institute_id, is_active) VALUES (%s,%s,%s,%s,%s,1)",
            (full_name, email, hashed, role, inst_id)
        )
        print(f"  [+] Created: {email}  (institute_id={inst_id})")
    else:
        print(f"  [~] Already exists: {email}")

db.commit()
db.close()
print("\n[DONE] Secretary accounts ready.")
