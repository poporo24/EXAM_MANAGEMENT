import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

# Check all admin and secretary accounts in Firebase
emails_to_check = [
    'admin@cca.edu.ph',
    'superadmin@cca.edu.ph',
]

import mysql.connector
conn = mysql.connector.connect(
    host='143.244.131.15',
    user='avnadmin',
    password='AVNS_0uijwdmnhsiqSaQyce-',
    database='defaultdb',
    port=15268
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT email, role, full_name FROM users WHERE role IN ('admin', 'secretary') ORDER BY role")
db_users = cursor.fetchall()
conn.close()

print("Checking admin/secretary accounts...")
print("-" * 60)
for user in db_users:
    email = user['email']
    try:
        fb_user = auth.get_user_by_email(email)
        print(f"[OK]     {email} ({user['role']}) - EXISTS in Firebase")
    except auth.UserNotFoundError:
        print(f"[MISSING] {email} ({user['role']}) - NOT IN FIREBASE!")
    except Exception as e:
        print(f"[ERROR]  {email}: {e}")
