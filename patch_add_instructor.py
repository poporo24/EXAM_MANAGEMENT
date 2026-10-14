import re
with open("system/database.py", "r", encoding="utf-8") as f:
    code = f.read()

pattern = r"cursor\.execute\(\"INSERT INTO users \(full_name, email, password, role, instructor_id\) VALUES \(\%s, \%s, \%s, \n'proctor', \%s\)\",\n\s*\(name, proctor_email, hashed, instructor_id\)\)\n\s*db\.commit\(\)\n\s*finally:\n\s*db\.close\(\)"
# Wait, string block is easier

old_str = """        cursor.execute("INSERT INTO users (full_name, email, password, role, instructor_id) VALUES (%s, %s, %s, 'proctor', %s)",
                       (name, proctor_email, hashed, instructor_id))
        db.commit()
    finally:
        db.close()"""
        
new_str = """        cursor.execute("INSERT INTO users (full_name, email, password, role, instructor_id) VALUES (%s, %s, %s, 'proctor', %s)",
                       (name, proctor_email, hashed, instructor_id))
        db.commit()
        return instructor_id
    finally:
        db.close()"""

if old_str in code:
    code = code.replace(old_str, new_str)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched add_instructor!")
else:
    print("Could not find old_str")
