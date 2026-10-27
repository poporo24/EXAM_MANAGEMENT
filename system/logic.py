"""
================================================================================
CCA EXAM MANAGEMENT SYSTEM - BUSINESS & SECURITY LOGIC
================================================================================
Module: system.logic
Purpose:
  Provides core authentication verification, cryptographic password hashing,
  NIST-compliant password strength validation, and role authorization helpers.
================================================================================
"""

import bcrypt
from system.database import open_db

def verify_login(email, password):
    """
    PURPOSE:
        Authenticates a user attempting to log into the system.
    INPUTS:
        email (str): Registered institutional email address
        password (str): Plaintext password submitted via login form
    RETURNS:
        dict: User record dictionary if credentials match and account is active
        'inactive': String flag if credentials match but account is pending approval
        None: If user is not found, password is invalid, or database connection fails
    """
    db = open_db()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            # Step 1: Query user record by email (supporting ñ transliteration to n)
            raw_email = (email or '').strip().lower()
            norm_email = raw_email.replace('ñ', 'n').replace('Ñ', 'n')
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = %s OR LOWER(email) = %s", (norm_email, raw_email))
            user = cursor.fetchone()

            if user and user.get('password'):
                # Step 2: Enforce strict bcrypt cryptographic verification
                password_ok = False
                try:
                    password_ok = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
                except (ValueError, TypeError, Exception):
                    password_ok = False

                if password_ok:
                    # Step 3: Block inactive accounts (e.g. students or proctors pending administrative approval)
                    if not user.get('is_active', 1):
                        return 'inactive'
                    return user
        finally:
            db.close()
    return None

def is_super_admin(session):
    """
    PURPOSE:
        Checks if the currently authenticated session possesses Super Admin privileges.
    INPUTS:
        session (dict): Flask session object
    RETURNS:
        bool: True if user is marked as super admin, False otherwise
    """
    return session.get('is_super_admin', False)

def hash_password(plain):
    """
    PURPOSE:
        Hashes a plaintext password using bcrypt with a securely generated salt.
    INPUTS:
        plain (str): Plaintext password
    RETURNS:
        str: UTF-8 decoded bcrypt hash string safe for database storage
    """
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def validate_password_strength(password):
    """
    PURPOSE:
        Validates password strength according to NIST SP 800-63B and institutional security policy.
    CRITERIA:
        - Minimum length: 8 characters
        - At least 1 uppercase letter (A-Z)
        - At least 1 numerical digit (0-9)
    INPUTS:
        password (str): Plaintext password to evaluate
    RETURNS:
        tuple: (is_valid: bool, error_message: str)
    """
    import re
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number (0-9)."
    return True, ""
