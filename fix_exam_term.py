with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

old_logic = """        cursor.execute("UPDATE exam_settings SET exam_term = %s, exam_semester = %s WHERE id = 1", (exam_term, exam_semester))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO exam_settings (id, exam_term, exam_semester) VALUES (1, %s, %s)", (exam_term, exam_semester))"""

new_logic = """        cursor.execute(
            "INSERT INTO exam_settings (id, exam_term, exam_semester) VALUES (1, %s, %s) "
            "ON DUPLICATE KEY UPDATE exam_term=VALUES(exam_term), exam_semester=VALUES(exam_semester)",
            (exam_term, exam_semester)
        )"""

if old_logic in db:
    db = db.replace(old_logic, new_logic)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Fixed exam_term bug")
else:
    print("Could not find old logic")
