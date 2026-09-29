import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import get_schedule_results, open_db, get_pending_exams, get_all_rooms, get_already_scheduled_slots, get_exam_period, get_system_settings
from system.scheduler import run_scheduler

def get_proctor_availability(): return {}
def get_active_instructors():
    db = open_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM instructors')
    i = c.fetchall()
    db.close()
    return i

period_start, period_end = get_exam_period()
pending = get_pending_exams()
rooms = get_all_rooms()
instructors = get_active_instructors()
booked = get_already_scheduled_slots()
settings = get_system_settings()

result = run_scheduler(
    pending_exams=pending,
    rooms=rooms,
    instructors=instructors,
    booked_slots=booked,
    period_start=period_start,
    period_end=period_end,
    proctor_availability={},
    settings=settings
)

scheduled_exams = booked + result['scheduled']
from datetime import datetime, timedelta
for exam in scheduled_exams:
    dt = exam.get('exam_date_time')
    if isinstance(dt, str): dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    exam['_dt'] = dt
    if 'duration_minutes' not in exam:
        exam['duration_minutes'] = 60

for i, a in enumerate(scheduled_exams):
    end_a = a['_dt'] + timedelta(minutes=a['duration_minutes'] or 60)
    for b in scheduled_exams[i+1:]:
        end_b = b['_dt'] + timedelta(minutes=b['duration_minutes'] or 60)
        overlaps = a['_dt'] < end_b and b['_dt'] < end_a
        sec_a = (a.get('section') or '').strip()
        sec_b = (b.get('section') or '').strip()
        if overlaps and sec_a and sec_a == sec_b:
            print(f"Conflict: Section {sec_a} has '{a['subject_name']}' and '{b['subject_name']}' at {a['_dt']}")
        
        if overlaps and a.get('room_id') and a['room_id'] == b.get('room_id'):
            print(f"Room Conflict: {a['room_id']} has '{a['subject_name']}' and '{b['subject_name']}' at {a['_dt']}")
            
        if overlaps and a.get('instructor_id') and a['instructor_id'] == b.get('instructor_id'):
            print(f"Inst Conflict: {a['instructor_id']} has '{a['subject_name']}' and '{b['subject_name']}' at {a['_dt']}")

