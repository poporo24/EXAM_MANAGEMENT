with open("app.py", "r", encoding="utf-8") as f:
    app = f.read()

old_login = """            if not user:
                flash("User not found in system.", "error")
                return redirect(url_for('login'))"""

new_login = """            if not user:
                flash("User not found in system.", "error")
                return redirect(url_for('login'))
                
            if not user.get('is_active', 1):
                flash("Your account is pending admin approval. You will be notified once it is activated.", "warning")
                return redirect(url_for('login'))"""

if old_login in app:
    app = app.replace(old_login, new_login)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app)
    print("Patched Firebase login to check is_active")
else:
    print("Could not find old_login")
