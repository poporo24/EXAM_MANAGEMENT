import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import open_db
from datetime import datetime as _dt, timedelta as _td

db = open_db()
cursor = db.cursor(dictionary=True)
new_start = _dt.strptime('2026-10-05T08:00', '%Y-%m-%dT%H:%M')
new_end = new_start + _td(minutes=60)

cursor.execute(
    "SELECT id, room_id, exam_date_time, duration_minutes FROM exams "
    "WHERE status='Scheduled' AND exam_date_time IS NOT NULL"
)
for row in cursor.fetchall():
    r_start = row['exam_date_time']
    if isinstance(r_start, str):
        r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
    
    # Let's print what duration_minutes is!
    # print(row['duration_minutes'])
    
    r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
    if new_start < r_end and r_start < new_end:
        print('Overlap!', row['id'], r_start, r_end, row['duration_minutes'])
        break
