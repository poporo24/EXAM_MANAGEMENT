import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

new_func = r'''def register_submit():
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
    result = register_user(full_name, email, password, role,
                           section=section, institute_id=institute_id)
    if result == 'ok':
        flash("Account created! Your registration is pending admin approval. You will be notified once it is activated.", "success")
        return redirect(url_for('login'))
    elif result == 'email_taken':
        flash("That email is already registered.", "danger")
        return redirect(url_for('register_page'))
    else:
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for('register_page'))
'''

app_content = re.sub(r'def register_submit\(\):.*?(?=# "?"? ADMIN DASHBOARD)', lambda m: new_func + '\n', app_content, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
print("Fixed register_submit completely")
