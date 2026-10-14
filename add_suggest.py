with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

new_func = """
def get_suggested_times(exam_id, duration_minutes, room_id=0, proctor_id=0):
    from datetime import datetime as _dt, timedelta as _td, date as _date, time as _time
    db_conn = open_db()
    if not db_conn: return []
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Get section for this exam
        cursor.execute("SELECT section, subject_type FROM exams WHERE id=%s", (exam_id,))
        this_exam = cursor.fetchone()
        section = this_exam['section'].strip() if this_exam and this_exam.get('section') else None
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major' if this_exam else True

        # Find the earliest scheduled exam to know when "Exam Week" is, or use today
        cursor.execute("SELECT MIN(exam_date_time) as min_dt FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL")
        min_row = cursor.fetchone()
        if min_row and min_row['min_dt']:
            start_date = min_row['min_dt']
            if isinstance(start_date, str):
                start_date = _dt.strptime(start_date, '%Y-%m-%d %H:%M:%S').date()
            else:
                start_date = start_date.date()
        else:
            start_date = _dt.today().date()
            
        if start_date < _dt.today().date():
            start_date = _dt.today().date()

        suggestions = []
        days_to_scan = 14
        
        # We need check_edit_conflicts function logic, but we can't easily call it in a loop without hitting the DB 100 times.
        # Let's fetch all scheduled exams ONCE into memory to make scanning ultra-fast!
        cursor.execute("SELECT id, section, room_id, instructor_id, exam_date_time, duration_minutes, subject_type FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s", (exam_id,))
        all_exams = cursor.fetchall()
        for ex in all_exams:
            if isinstance(ex['exam_date_time'], str):
                ex['exam_date_time'] = _dt.strptime(ex['exam_date_time'], '%Y-%m-%d %H:%M:%S')
                
        # Also get proctor availability if a proctor is specified
        proctor_avail = get_proctor_availability()

        for day_offset in range(days_to_scan):
            current_date = start_date + _td(days=day_offset)
            # Skip Sundays
            if current_date.weekday() == 6: continue
            
            # Scan from 7 AM to 5 PM
            for hour in range(7, 18):
                # We will check top of the hour and half past
                for minute in (0, 30):
                    slot_start = _dt.combine(current_date, _time(hour, minute))
                    slot_end = slot_start + _td(minutes=duration_minutes)
                    
                    if slot_end.time() > _time(20, 0): # Don't go past 8 PM
                        continue
                        
                    conflict = False
                    day_major = 0
                    day_minor = 0
                    
                    for ex in all_exams:
                        ex_start = ex['exam_date_time']
                        ex_end = ex_start + _td(minutes=ex['duration_minutes'] or 60)
                        
                        # 1. Section conflict
                        if section and ex['section'] == section:
                            # Time overlap with 1 hr break
                            buf_start = slot_start - _td(hours=1)
                            buf_end = slot_end + _td(hours=1)
                            if buf_start < ex_end and ex_start < buf_end:
                                conflict = True
                                break
                            # Daily limits
                            if ex_start.date() == current_date:
                                if (ex.get('subject_type') or 'Major') == 'Major': day_major += 1
                                else: day_minor += 1
                        
                        # 2. Room conflict
                        if room_id and ex['room_id'] == room_id:
                            if slot_start < ex_end and ex_start < slot_end:
                                conflict = True
                                break
                                
                        # 3. Proctor conflict
                        if proctor_id and ex['instructor_id'] == proctor_id:
                            if slot_start < ex_end and ex_start < slot_end:
                                conflict = True
                                break
                                
                    if conflict: continue
                    
                    # Section daily limits
                    if section:
                        minor_limit = 4 - day_major
                        if is_major and day_major >= 3: conflict = True
                        if not is_major and day_minor >= minor_limit: conflict = True
                        if day_major + day_minor >= 3: conflict = True
                    if conflict: continue
                    
                    # 4. Proctor Availability explicitly declared
                    if proctor_id:
                        avail_entries = proctor_avail.get(proctor_id)
                        if avail_entries:
                            has_entry = False
                            time_match = False
                            for ent in avail_entries:
                                if ent['date'] == current_date:
                                    has_entry = True
                                    if slot_start.time() >= ent['start_time'] and slot_end.time() <= ent['end_time']:
                                        time_match = True
                                        break
                            if has_entry and not time_match:
                                conflict = True
                    if conflict: continue
                    
                    # It's a valid slot!
                    suggestions.append({
                        'datetime': slot_start.strftime('%Y-%m-%dT%H:%M'),
                        'label': slot_start.strftime('%a, %b %d, %Y - %I:%M %p')
                    })
                    
                    # Only return up to 10 suggestions to avoid overwhelming the UI
                    if len(suggestions) >= 10:
                        return suggestions
                        
        return suggestions
    finally:
        db_conn.close()
"""

if "def get_suggested_times" not in db:
    db = db + "\n" + new_func
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Added get_suggested_times")
else:
    print("Already exists")
