html_path = 'template/login.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_error_logic = '''        let msg = "Error: " + error.message;
        if (error.code === 'auth/user-not-found') msg = "No user found with this email.";
        if (error.code === 'auth/wrong-password') msg = "Incorrect password.";
        if (error.code === 'auth/too-many-requests') msg = "Account temporarily locked due to many failed attempts.";'''

new_error_logic = '''        let msg = "An error occurred during login. Please try again.";
        if (error.code === 'auth/invalid-credential') msg = "Wrong email or password.";
        if (error.code === 'auth/user-not-found') msg = "Wrong email or password.";
        if (error.code === 'auth/wrong-password') msg = "Wrong email or password.";
        if (error.code === 'auth/too-many-requests') msg = "Account temporarily locked due to many failed attempts.";'''

if old_error_logic in html:
    html = html.replace(old_error_logic, new_error_logic)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed Firebase error messages!")
else:
    print("Could not find the exact error logic block. Attempting regex...")
    import re
    pattern = re.compile(r'let msg = "Error: " \+ error\.message;.*?if \(error\.code === .auth/too-many-requests.\) msg = "Account temporarily locked due to many failed attempts.";', re.DOTALL)
    match = pattern.search(html)
    if match:
        html = html.replace(match.group(0), new_error_logic)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("Fixed via regex!")
    else:
        print("Still not found.")
