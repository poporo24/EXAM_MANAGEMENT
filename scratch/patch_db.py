with open('system/database.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        proctor_password = "proctor123"

        cursor.execute("SELECT id FROM users WHERE email = %s", (proctor_email,))
        if cursor.fetchone():
            email_name = clean_email_name(name)
            proctor_email = f"{email_name}.{instructor_id}@cca.edu.ph"

        hashed = hash_password(proctor_password)"""

replacement = """        proctor_password = "proctor123"

        cursor.execute("SELECT id FROM users WHERE email = %s", (proctor_email,))
        if cursor.fetchone():
            email_name = clean_email_name(name)
            proctor_email = f"{email_name}.{instructor_id}@cca.edu.ph"

        global _cached_proctor_pw_hash
        if '_cached_proctor_pw_hash' not in globals() or not _cached_proctor_pw_hash:
            _cached_proctor_pw_hash = hash_password(proctor_password)
        hashed = _cached_proctor_pw_hash"""

if target in text:
    text = text.replace(target, replacement)
    with open('system/database.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully patched system/database.py")
else:
    print("Target not found")
