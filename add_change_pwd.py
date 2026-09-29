app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_route = '''
# --- SELF CHANGE PASSWORD (Admin/Superadmin) ---
@app.route("/settings/change_password", methods=["POST"])
def admin_self_change_password():
    guard = require_role('admin')
    if guard: return guard

    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password or not confirm_password:
        flash("All fields are required.", "danger")
        return redirect(url_for('settings'))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('settings'))

    # Strict constraints (same as registration)
    import re
    if len(new_password) < 8 or not re.search(r"[A-Z]", new_password) or not re.search(r"\d", new_password):
        flash("Password must be at least 8 characters long, contain an uppercase letter, and a number.", "danger")
        return redirect(url_for('settings'))

    user_id = session.get('user_id')
    email = session.get('email')

    # Verify current password directly via Firebase REST API for 100% accuracy
    import requests
    import json
    API_KEY = "AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwhE"
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    resp = requests.post(url, json={
        "email": email,
        "password": current_password,
        "returnSecureToken": True
    })

    if resp.status_code != 200:
        # Fallback to check local DB if Firebase fails
        db = open_db()
        if db:
            try:
                import bcrypt as _bcrypt
                c = db.cursor(dictionary=True)
                c.execute("SELECT password FROM users WHERE id = %s", (user_id,))
                user = c.fetchone()
                if not user:
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for('settings'))
                try:
                    current_ok = _bcrypt.checkpw(current_password.encode(), user['password'].encode())
                except ValueError:
                    current_ok = (current_password == user['password'])
                if not current_ok:
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for('settings'))
            finally:
                db.close()
        else:
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('settings'))

    # Update in Firebase
    try:
        from firebase_admin import auth as fb_auth
        fb_user = fb_auth.get_user_by_email(email)
        fb_auth.update_user(fb_user.uid, password=new_password)
    except Exception as e:
        print(f"Firebase password update skipped: {e}")

    # Update in MySQL DB
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c = db.cursor()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            db.commit()
            flash("Your password has been successfully updated.", "success")
        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")
        finally:
            db.close()

    return redirect(url_for('settings'))
'''

if 'admin_self_change_password' not in content:
    # Insert right before settings page rendering
    target = '@app.route("/settings", methods=["GET"])'
    content = content.replace(target, new_route + '\n' + target)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added /settings/change_password route!")
else:
    print("Route already exists!")
