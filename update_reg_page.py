import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# Update register_page in app.py
old_reg_page = '''def register_page():
    if 'user_id' in session:
        return _redirect_by_role()
    institutes = get_all_institutes()
    return render_template("register.html", institutes=institutes)'''

new_reg_page = '''def register_page():
    if 'user_id' in session:
        return _redirect_by_role()
    institutes = get_all_institutes()
    
    # Get distinct sections
    sections = []
    from system.database import open_db
    db = open_db()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT section FROM users WHERE section IS NOT NULL AND section != '' ORDER BY section")
            sections = [r[0] for r in cursor.fetchall()]
        finally:
            db.close()
            
    return render_template("register.html", institutes=institutes, sections=sections)'''

app_content = app_content.replace(old_reg_page, new_reg_page)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Updated app.py")
