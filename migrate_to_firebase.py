import firebase_admin
from firebase_admin import credentials, auth
import mysql.connector

# Connect DB
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="cca_exam_management_db"
)
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT id, email, password FROM users WHERE password IS NOT NULL AND password != ''")
users_db = cursor.fetchall()

# Init Firebase
cred = credentials.Certificate('firebase_credentials.json')
firebase_admin.initialize_app(cred)

users_to_import = []
for u in users_db:
    # Firebase uid must be string
    uid = str(u['id'])
    email = u['email']
    pwd_hash = u['password'].encode('utf-8')
    
    users_to_import.append(
        auth.ImportUserRecord(
            uid=uid,
            email=email,
            password_hash=pwd_hash
        )
    )

# Import in batches of 1000
try:
    hash_alg = auth.UserImportHash.bcrypt()
    result = auth.import_users(users_to_import, hash_alg=hash_alg)
    print(f"Successfully imported {result.success_count} users.")
    for err in result.errors:
        print(f"Error importing user at index {err.index}: {err.reason}")
except Exception as e:
    print(f"Migration error: {e}")
