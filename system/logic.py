from system.database import open_db

def verify_login(email, password):
    """Authenticate a user and return their full record (includes role, instructor_id)."""
    db = open_db()
    if db:
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()
        db.close()
        return user
    return None