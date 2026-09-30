with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

db = db.replace(
    "FROM users WHERE role='student' AND is_active=0",
    "FROM users WHERE role IN ('student', 'proctor') AND is_active=0"
)
db = db.replace("def get_pending_students():", "def get_pending_users():")

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)

with open("app.py", "r", encoding="utf-8") as f:
    app_c = f.read()
    
app_c = app_c.replace("get_pending_students", "get_pending_users")
app_c = app_c.replace("pending_students = get_pending_students()", "pending_users = get_pending_users()")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_c)
print("Patched pending users")
