import system.database as db
exams = db.get_schedule_results()
baels_exams = [e for e in exams if e['section'] == 'BAELS 301']
for e in baels_exams:
    res = db.get_full_auto_schedule(e['id'], 60, sync_all=False)
    if res and res['datetime'] == '2026-10-17T07:00':
        print(f"Auto-schedule gave 2026-10-17T07:00 for exam {e['id']}")
