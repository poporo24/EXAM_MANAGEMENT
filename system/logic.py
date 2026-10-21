import bcrypt
from system.database import open_db

def verify_login(email, password):
    db = open_db()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and user.get('password'):
                # Enforce strict bcrypt cryptographic verification (eliminate plaintext fallback)
                password_ok = False
                try:
                    password_ok = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
                except (ValueError, TypeError, Exception):
                    password_ok = False

                if password_ok:
                    # Block inactive accounts (students/proctors pending approval)
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

def validate_password_strength(password):
    """
    Validates password strength according to NIST SP 800-63B and institutional security policy:
    - Minimum 8 characters
    - At least 1 uppercase letter (A-Z)
    - At least 1 number (0-9)
    Returns (is_valid: bool, error_message: str)
    """
    import re
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number (0-9)."
    return True, ""
