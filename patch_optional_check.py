with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

# Make room and instructor optional for conflict checking
old_check = "def check_edit_conflicts(exam_id, new_room_id, new_instructor_id, new_datetime_str, duration_minutes):"
new_check = "def check_edit_conflicts(exam_id, new_room_id, new_instructor_id, new_datetime_str, duration_minutes):" # Keep signature

# In database.py:
db = db.replace(
    "cursor.execute(\"SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE room_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL\", (new_room_id, exam_id))",
    "if new_room_id:\n            cursor.execute(\"SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE room_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL\", (new_room_id, exam_id))"
)
db = db.replace(
    "cursor.execute(\"SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE instructor_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL\", (new_instructor_id, exam_id))",
    "if new_instructor_id:\n            cursor.execute(\"SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE instructor_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL\", (new_instructor_id, exam_id))"
)

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Patched check_edit_conflicts in DB")
