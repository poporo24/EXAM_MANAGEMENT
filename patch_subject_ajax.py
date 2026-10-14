with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

old_logic = """        # Section conflict: same section cannot have two exams at the same time
        # + per-section daily exam limits (max 2 major, max 3 minor, max 3 total)
        cursor.execute(
            "SELECT section, subject_type FROM exams WHERE id=%s", (exam_id,)
        )"""

new_logic = """        # Subject conflict: check if sister sections are scheduled at different times
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
                        break

        # Section conflict: same section cannot have two exams at the same time
        # + per-section daily exam limits (max 2 major, max 3 minor, max 3 total)
        cursor.execute(
            "SELECT section, subject_type FROM exams WHERE id=%s", (exam_id,)
        )"""

if old_logic in db:
    db = db.replace(old_logic, new_logic)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Patched check_edit_conflicts for Subject integrity")
else:
    print("Could not find old logic block!")
