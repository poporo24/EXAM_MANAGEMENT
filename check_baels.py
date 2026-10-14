import system.database as db
exams = db.get_schedule_results()
for e in exams:
    if e['section'] == 'BAELS 301' and e['status'] == 'Scheduled':
        print(f"Exam {e['id']}: {e['subject_name']} at {e['exam_date_time']}")
