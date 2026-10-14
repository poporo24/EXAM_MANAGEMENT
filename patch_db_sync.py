with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()
    
import re
pattern = r"def apply_exam_edit\(exam_id, new_room_id, new_instructor_id, new_datetime_str\):.*?db\.commit\(\)"

new_func = """def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str, sync_all=False):
    from datetime import datetime as _dt
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        try:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')

        cursor_r.execute(
            "SELECT subject_name, section, instructor_id, room_id, exam_date_time FROM exams WHERE id=%s",
            (exam_id,)
        )
        old = cursor_r.fetchone() or {}
        old_instructor_id = old.get('instructor_id')
        section  = (old.get('section') or '').strip()
        subject  = old.get('subject_name') or 'Exam'
        dt_str   = new_dt.strftime('%b %d, %Y %I:%M %p')

        sister_ids = []
        if sync_all and subject:
            cursor_r.execute("SELECT id FROM exams WHERE subject_name=%s AND id!=%s", (subject, exam_id))
            sister_ids = [r['id'] for r in cursor_r.fetchall()]

        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_dt, exam_id)
        )
        
        if sync_all and sister_ids:
            format_strings = ','.join(['%s'] * len(sister_ids))
            cursor.execute(
                f"UPDATE exams SET exam_date_time=%s, status='Scheduled' WHERE id IN ({format_strings})",
                [new_dt] + sister_ids
            )
        db.commit()"""

db = re.sub(pattern, new_func, db, flags=re.DOTALL)

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Patched apply_exam_edit using regex")
