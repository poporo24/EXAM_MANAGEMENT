with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

import re
# Find all occurrences of the new logic block
block = """        # Subject conflict: check if sister sections are scheduled at different times
        cursor.execute("SELECT subject_name FROM exams WHERE id=%s", (exam_id,))
        sub_row = cursor.fetchone()
        if sub_row and sub_row.get('subject_name'):
            subj_name = sub_row['subject_name'].strip().lower()
            if subj_name:
                cursor.execute(
                    "SELECT section, exam_date_time FROM exams WHERE LOWER(TRIM(subject_name))=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL",
                    (subj_name, exam_id)
                )
                for row in cursor.fetchall():
                    s_time = row['exam_date_time']
                    if isinstance(s_time, str): s_time = _dt.strptime(s_time, '%Y-%m-%d %H:%M:%S')
                    # We just check if the new_start is exactly the same as the sister section
                    if new_start != s_time:
                        conflicts.append(f"? Integrity Risk: Section '{row['section']}' is taking this exam at {s_time}. (Use 'Sync ALL' to avoid this).")
                        # Only add this conflict warning once to avoid spam
                        break"""

# Count occurrences
if db.count(block) > 1:
    # replace all but the last one
    db = db.replace(block, "")
    db = db.replace("        # Section conflict: same section cannot have two exams at the same time", block + "\n\n        # Section conflict: same section cannot have two exams at the same time")
    
with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Removed duplicate")
