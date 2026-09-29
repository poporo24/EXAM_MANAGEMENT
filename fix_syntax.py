import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Let's extract everything BEFORE register_submit and everything AFTER the dashboard route
part1 = app_content.split('def register_submit():')[0]
part2 = app_content.split('@app.route("/dashboard")')[1]

clean_func = '''def register_submit():
    full_name    = request.form.get("full_name", "").strip()
    email        = request.form.get("email", "").strip()
    password     = request.form.get("password", "").strip()
    section      = request.form.get("section", "").strip()
    institute_id = request.form.get("institute_id") or None
    role         = request.form.get("role", "student").strip()
    
    if role not in ['student', 'proctor']:
        role = 'student'
        
    if not email.endswith("@cca.edu.ph"):
        flash("Registration is restricted to @cca.edu.ph email addresses only.", "danger")
        return redirect(url_for('register_page'))
        
    import re as regex
    if len(password) < 8 or not regex.search(r'[A-Z]', password) or not regex.search(r'\d', password):
        flash("Password must be at least 8 characters long and contain at least one uppercase letter and one number.", "danger")
        return redirect(url_for('register_page'))

    if not full_name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('register_page'))
        
    # Check if user already exists in MySQL
    user_exists = get_user_by_email(email)
    if user_exists:
        flash("That email is already registered.", "danger")
        return redirect(url_for('register_page'))
        
    # Try creating user in Firebase FIRST so we catch Firebase duplicates
    try:
        from firebase_admin import auth as fb_auth
        fb_auth.create_user(email=email, password=password, display_name=full_name)
    except fb_auth.EmailAlreadyExistsError:
        flash("That email is already registered in the cloud auth system.", "danger")
        return redirect(url_for('register_page'))
    except Exception as e:
        flash(f"Cloud Auth Error: {str(e)}", "danger")
        return redirect(url_for('register_page'))

    # Create user in local MySQL
    result = register_user(full_name, email, password, role, section=section, institute_id=institute_id)
                           
    if result == 'ok':
        flash("Account created! Your registration is pending admin approval. You will be notified once it is activated.", "success")
        return redirect(url_for('login'))
    else:
        flash("Something went wrong saving to the local database.", "danger")
        return redirect(url_for('register_page'))

# --- ADMIN DASHBOARD ---

@app.route("/dashboard")'''

new_content = part1 + clean_func + part2

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed syntax error")
