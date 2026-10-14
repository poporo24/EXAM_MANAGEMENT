with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

# We need to find apply_exam_edit
old_def = """def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str, duration_minutes, force=False):"""
new_def = """def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str, duration_minutes, force=False, sync_all=False):"""
db = db.replace(old_def, new_def)

# Find the part where it updates the single exam:
old_update = """        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, duration_minutes=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_datetime_str, duration_minutes, exam_id)
        )
        db.commit()"""
new_update = """        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, duration_minutes=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_datetime_str, duration_minutes, exam_id)
        )
        
        if sync_all:
            # Get the subject name
            cursor.execute("SELECT subject_name FROM exams WHERE id=%s", (exam_id,))
            row = cursor.fetchone()
            if row and row['subject_name']:
                subj = row['subject_name']
                # Get sister sections
                cursor.execute("SELECT id FROM exams WHERE subject_name=%s AND id!=%s", (subj, exam_id))
                sisters = cursor.fetchall()
                
                # Auto-assign for each sister
                for sis in sisters:
                    sis_id = sis['id']
                    # Use get_full_auto_schedule but pass the new_datetime_str to force it to pick that time
                    # Actually, a simpler way is to just set their time, and clear their room/proctor, setting them to Pending.
                    # Or we can do a mini room/proctor search for that exact datetime.
                    # Let's just set the date/time, and clear room/proctor so the admin can fill them in, OR if they used Auto-Schedule, we should assign them properly.
                    # Since this is a massive AI patch, let's just do a quick greedy assignment!
                    
                    # 1. Find a free room
                    cursor.execute("SELECT id FROM rooms WHERE id NOT IN (SELECT room_id FROM exams WHERE exam_date_time=%s AND room_id IS NOT NULL)", (new_datetime_str,))
                    free_room = cursor.fetchone()
                    r_id = free_room['id'] if free_room else None
                    
                    # 2. Find a free proctor
                    cursor.execute("SELECT id FROM instructors WHERE status='Active' AND id NOT IN (SELECT instructor_id FROM exams WHERE exam_date_time=%s AND instructor_id IS NOT NULL)", (new_datetime_str,))
                    free_proc = cursor.fetchone()
                    p_id = free_proc['id'] if free_proc else None
                    
                    status = 'Scheduled' if (r_id and p_id) else 'Pending'
                    
                    cursor.execute(
                        "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, duration_minutes=%s, status=%s WHERE id=%s",
                        (r_id, p_id, new_datetime_str, duration_minutes, status, sis_id)
                    )

        db.commit()"""
db = db.replace(old_update, new_update)

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Patched apply_exam_edit")
