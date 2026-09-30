import re

with open("system/database.py", "r", encoding="utf-8") as f:
    code = f.read()

old_delete = """def delete_user(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        db.commit()
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()"""

new_delete = """def delete_user(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT email FROM users WHERE id=%s", (id,))
        user = cursor.fetchone()
        if not user:
            return "User not found"
        email = user['email']
        
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        db.commit()
        
        # Also delete from Firebase Auth so they can re-register if rejected
        try:
            from firebase_admin import auth as fb_auth
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.delete_user(fb_user.uid)
        except Exception:
            pass # Ignore if not found in Firebase
            
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()"""

if old_delete in code:
    code = code.replace(old_delete, new_delete)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched delete_user")
else:
    print("Could not find exact old_delete")
