import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import open_db
from datetime import datetime as _dt, timedelta as _td

db = open_db()
cursor = db.cursor(dictionary=True)
new_start = _dt.strptime('2026-10-05T08:00', '%Y-%m-%dT%H:%M')
new_end = new_start + _td(minutes=60)

cursor.execute("SELECT r.id, r.room_name as name, r.capacity FROM rooms r ORDER BY r.room_name")
all_rooms = cursor.fetchall()

cursor.execute(
    "SELECT room_id, instructor_id, exam_date_time, duration_minutes FROM exams "
    "WHERE status='Scheduled' AND exam_date_time IS NOT NULL"
)
busy_rooms = set()
for row in cursor.fetchall():
    r_start = row['exam_date_time']
    if isinstance(r_start, str):
        r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
    r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
    if new_start < r_end and r_start < new_end:
        if row['room_id']: busy_rooms.add(row['room_id'])

print('All rooms count:', len(all_rooms))
print('Busy rooms count:', len(busy_rooms))
