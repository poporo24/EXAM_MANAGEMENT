with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

db = db.replace(r'\"\"\"', '"""')

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
