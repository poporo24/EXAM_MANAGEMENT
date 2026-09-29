import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# I will just write a precise replacement block
import textwrap

correct_logic = '''
    if not email.endswith("@cca.edu.ph"):
        flash("Registration is restricted to @cca.edu.ph email addresses only.", "danger")
        return redirect(url_for('register_page'))
        
    import re
    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        flash("Password must be at least 8 characters long and contain at least one uppercase letter and one number.", "danger")
        return redirect(url_for('register_page'))

    if not full_name or not email or not password:
'''
# I need to find the mess I made and replace it
# The mess looks like:
mess = '''    if not email.endswith("@cca.edu.ph"):
        flash("Registration is restricted to @cca.edu.ph email addresses only.", "danger")
        return redirect(url_for('register_page'))
        
    import re
    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        flash("Password must be at least 8 characters long and contain at least one uppercase letter and one number.", "danger")
        return redirect(url_for('register_page'))

    if not full_name or not email or not password:'''

app_content = app_content.replace(mess, correct_logic.lstrip('\n'))

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
print("Fixed app.py formatting")
