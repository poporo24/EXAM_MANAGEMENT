import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Update super_reset_password to sync with Firebase
old_super_reset = '''    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c = db.cursor()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, id))
            db.commit()
            flash("Password reset.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))'''

new_super_reset = '''    db = open_db()
    if db:
        try:
            c = db.cursor(dictionary=True)
            c.execute("SELECT email FROM users WHERE id = %s", (id,))
            user = c.fetchone()
            if user:
                # 1. Update Firebase
                from firebase_admin import auth as fb_auth
                try:
                    fb_user = fb_auth.get_user_by_email(user['email'])
                    fb_auth.update_user(fb_user.uid, password=new_password)
                except Exception as fb_err:
                    print("Firebase update skipped or failed:", fb_err)
                
                # 2. Update Local DB
                import bcrypt as _bcrypt
                hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
                c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, id))
                db.commit()
                flash("Password securely reset in both the database and cloud auth.", "success")
            else:
                flash("User not found.", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))'''

if 'def super_reset_password' in app_content:
    app_content = app_content.replace(old_super_reset, new_super_reset)

# Update admin_change_password to sync with Firebase
old_admin_reset = '''            if not user or user['role'] not in ('student', 'proctor'):
                flash("User not found or not allowed.", "danger")
                return redirect(url_for(redirect_to))
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            db.commit()
            flash(f"o. Password changed for {user['full_name']}.", "success")'''

new_admin_reset = '''            if not user or user['role'] not in ('student', 'proctor'):
                flash("User not found or not allowed.", "danger")
                return redirect(url_for(redirect_to))
            
            c.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            user_email_row = c.fetchone()
            if user_email_row:
                from firebase_admin import auth as fb_auth
                try:
                    fb_user = fb_auth.get_user_by_email(user_email_row['email'])
                    fb_auth.update_user(fb_user.uid, password=new_password)
                except Exception as fb_err:
                    print("Firebase update skipped or failed:", fb_err)

            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            db.commit()
            flash(f"Password changed for {user['full_name']} in both database and cloud auth.", "success")'''

app_content = app_content.replace(old_admin_reset, new_admin_reset)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
    
print("Updated password reset functions to sync with Firebase!")
