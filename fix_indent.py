with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

db = db.replace("        if new_room_id:\n            if new_room_id:\n            cursor.execute", "        if new_room_id:\n            cursor.execute")
db = db.replace("        if new_instructor_id:\n            if new_instructor_id:\n            cursor.execute", "        if new_instructor_id:\n            cursor.execute")

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Fixed IndentationError")
