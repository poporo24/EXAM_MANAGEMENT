with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

old_def = "def get_full_auto_schedule(exam_id, duration_minutes):"
new_def = "def get_full_auto_schedule(exam_id, duration_minutes, sync_all=False):"

db = db.replace(old_def, new_def)

# We need to find the subject_name and count sister exams
old_subject = "cursor.execute(\"SELECT section, subject_type, institute_id FROM exams WHERE id=%s\", (exam_id,))"
new_subject = """cursor.execute("SELECT subject_name, section, subject_type, institute_id FROM exams WHERE id=%s", (exam_id,))"""
db = db.replace(old_subject, new_subject)

old_vars = """section = this_exam['section'].strip() if this_exam.get('section') else None
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major'
        institute_id = this_exam.get('institute_id')"""
new_vars = """section = this_exam['section'].strip() if this_exam.get('section') else None
        subject_name = this_exam['subject_name']
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major'
        institute_id = this_exam.get('institute_id')
        
        sister_sections = []
        if sync_all and subject_name:
            cursor.execute("SELECT id, section FROM exams WHERE subject_name=%s AND id!=%s", (subject_name, exam_id))
            sister_sections = cursor.fetchall()
        
        total_sections_needed = 1 + len(sister_sections)"""
db = db.replace(old_vars, new_vars)

# In the loop, we need to check if there are enough rooms/proctors
old_check = """if not free_insts: continue
                    
                    # We found a slot!
                    # Pick a room (just the first available one, or random to distribute load)
                    chosen_room = random.choice(free_rooms)['id']"""
new_check = """if len(free_insts) < total_sections_needed or len(free_rooms) < total_sections_needed: continue
                    
                    # We found a slot!
                    # Pick a room (just the first available one, or random to distribute load)
                    chosen_room = random.choice(free_rooms)['id']"""
db = db.replace(old_check, new_check)

# Also in the loop, check section conflicts for ALL sister sections
old_section_conflict = """if section and ex['section'] == section:"""
new_section_conflict = """my_sections = [section] + [s['section'] for s in sister_sections if s['section']]
                        if ex['section'] in my_sections:"""
db = db.replace(old_section_conflict, new_section_conflict)

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)
print("Patched database auto schedule")
