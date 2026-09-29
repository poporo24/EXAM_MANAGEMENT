import re

# --- Update app.py ---
app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

validation_logic = '''    if not email.endswith("@cca.edu.ph"):
        flash("Registration is restricted to @cca.edu.ph email addresses only.", "danger")
        return redirect(url_for('register_page'))
        
    import re
    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        flash("Password must be at least 8 characters long and contain at least one uppercase letter and one number.", "danger")
        return redirect(url_for('register_page'))
'''

app_content = app_content.replace('if not full_name or not email or not password:', validation_logic + '\n    if not full_name or not email or not password:')

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

# --- Update register.html ---
reg_path = 'template/register.html'
with open(reg_path, 'r', encoding='utf-8') as f:
    reg_content = f.read()

reg_content = reg_content.replace(
    'type="email" name="email" id="email" required',
    'type="email" name="email" id="email" required pattern=".*@cca\.edu\.ph$" title="Must be a valid @cca.edu.ph email address"'
)

reg_content = reg_content.replace(
    'placeholder="you@example.com"',
    'placeholder="student@cca.edu.ph"'
)

reg_content = reg_content.replace(
    'type="password" name="password" id="password" required',
    'type="password" name="password" id="password" required minlength="8" pattern="(?=.*\d)(?=.*[A-Z]).{8,}" title="Password must be at least 8 characters long and contain at least one uppercase letter and one number."'
)

with open(reg_path, 'w', encoding='utf-8') as f:
    f.write(reg_content)

print("Added security constraints!")
