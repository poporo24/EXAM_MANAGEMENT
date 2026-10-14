import system.database as db
exams = db.get_schedule_results()
for e in exams:
    if 'ELT 2' in (e.get('subject_name') or ''):
        print(f"Exam {e['id']}: {e['subject_name']} for {e['section']} at {e['exam_date_time']}")
