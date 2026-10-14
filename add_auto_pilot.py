with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

new_func = """
def get_full_auto_schedule(exam_id, duration_minutes):
    from datetime import datetime as _dt, timedelta as _td, date as _date, time as _time
    import random
    db_conn = open_db()
    if not db_conn: return None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Get section for this exam
        cursor.execute("SELECT section, subject_type, institute_id FROM exams WHERE id=%s", (exam_id,))
        this_exam = cursor.fetchone()
        if not this_exam: return None
        
        section = this_exam['section'].strip() if this_exam.get('section') else None
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major'
        institute_id = this_exam.get('institute_id')

        # Find the start date
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

        days_to_scan = 14
        
        # Load all exams
        cursor.execute("SELECT id, section, room_id, instructor_id, exam_date_time, duration_minutes, subject_type FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s", (exam_id,))
        all_exams = cursor.fetchall()
        for ex in all_exams:
            if isinstance(ex['exam_date_time'], str):
                ex['exam_date_time'] = _dt.strptime(ex['exam_date_time'], '%Y-%m-%d %H:%M:%S')
                
        # Load all rooms and proctors
        cursor.execute("SELECT id, room_name, capacity FROM rooms ORDER BY room_name")
        all_rooms = cursor.fetchall()
        
        # Prefer proctors from the same institute if possible, but load all
        cursor.execute("SELECT id, name, institute_id FROM instructors WHERE status='Active' ORDER BY name")
        all_insts = cursor.fetchall()
        
        proctor_avail = get_proctor_availability()

        for day_offset in range(days_to_scan):
            current_date = start_date + _td(days=day_offset)
            if current_date.weekday() == 6: continue # skip Sunday
            
            for hour in range(7, 18):
                for minute in (0, 30):
                    slot_start = _dt.combine(current_date, _time(hour, minute))
                    slot_end = slot_start + _td(minutes=duration_minutes)
                    
                    if slot_end.time() > _time(20, 0): continue
                        
                    section_conflict = False
                    day_major = 0
                    day_minor = 0
                    
                    busy_rooms = set()
                    busy_insts = set()
                    
                    for ex in all_exams:
                        ex_start = ex['exam_date_time']
                        ex_end = ex_start + _td(minutes=ex['duration_minutes'] or 60)
                        
                        # Time overlap checks
                        buf_start = slot_start - _td(hours=1)
                        buf_end = slot_end + _td(hours=1)
                        
                        overlap_strict = (slot_start < ex_end and ex_start < slot_end)
                        overlap_buffer = (buf_start < ex_end and ex_start < buf_end)
                        
                        if section and ex['section'] == section:
                            if overlap_buffer:
                                section_conflict = True
                                break
                            if ex_start.date() == current_date:
                                if (ex.get('subject_type') or 'Major') == 'Major': day_major += 1
                                else: day_minor += 1
                                
                        if overlap_strict:
                            if ex['room_id']: busy_rooms.add(ex['room_id'])
                            if ex['instructor_id']: busy_insts.add(ex['instructor_id'])
                                
                    if section_conflict: continue
                    
                    if section:
                        minor_limit = 4 - day_major
                        if is_major and day_major >= 3: continue
                        if not is_major and day_minor >= minor_limit: continue
                        if day_major + day_minor >= 3: continue
                    
                    # Find a free room
                    free_rooms = [r for r in all_rooms if r['id'] not in busy_rooms]
                    if not free_rooms: continue
                    
                    # Find a free proctor
                    free_insts = []
                    for i in all_insts:
                        if i['id'] in busy_insts: continue
                        
                        # Check explicitly declared availability
                        avail_entries = proctor_avail.get(i['id'])
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
                                continue # declared unavailable
                        
                        free_insts.append(i)
                        
                    if not free_insts: continue
                    
                    # We found a slot!
                    # Pick a room (just the first available one, or random to distribute load)
                    chosen_room = random.choice(free_rooms)['id']
                    
                    # Pick a proctor (prefer same institute)
                    same_inst = [i for i in free_insts if i['institute_id'] == institute_id]
                    if same_inst:
                        chosen_proctor = random.choice(same_inst)['id']
                    else:
                        chosen_proctor = random.choice(free_insts)['id']
                        
                    return {
                        'datetime': slot_start.strftime('%Y-%m-%dT%H:%M'),
                        'room_id': chosen_room,
                        'instructor_id': chosen_proctor
                    }
                    
        return None
    finally:
        db_conn.close()
"""

if "def get_full_auto_schedule" not in db:
    db = db + "\n" + new_func
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Added get_full_auto_schedule")
else:
    print("Already exists")
