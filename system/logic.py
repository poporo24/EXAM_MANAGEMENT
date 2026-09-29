import bcrypt
from system.database import open_db

def verify_login(email, password):
    db = open_db()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and user['password']:
                # Check password
                password_ok = False
                try:
                    password_ok = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
                except ValueError:
                    password_ok = (password == user['password'])

                if password_ok:
                    # Block inactive accounts (students pending approval)
                    if not user.get('is_active', 1):
                        return 'inactive'
                    return user
        finally:
            db.close()
    return None

def is_super_admin(session):
    return session.get('is_super_admin', False)

def hash_password(plain):
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')