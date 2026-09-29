import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import get_schedule_results, open_db, unschedule_exams, get_pending_exams, get_all_rooms, get_already_scheduled_slots, get_exam_period, apply_schedule_results, get_system_settings
from system.scheduler import run_scheduler

def get_proctor_availability():
    return {}
def get_active_instructors():
    db = open_db()
    c = db.cursor(dictionary=True)
    c.execute('SELECT * FROM instructors')
    i = c.fetchall()
    db.close()
    return i

# get conflicts logic
all_exams = get_schedule_results()
scheduled_exams = [e for e in all_exams if e['status'] == 'Scheduled']
from datetime import datetime, timedelta
for exam in scheduled_exams:
    dt = exam['exam_date_time']
    if isinstance(dt, str): dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    exam['_dt'] = dt

conflict_ids = set()
for i, a in enumerate(scheduled_exams):
    end_a = a['_dt'] + timedelta(minutes=a['duration_minutes'] or 60)
    for b in scheduled_exams[i+1:]:
        end_b = b['_dt'] + timedelta(minutes=b['duration_minutes'] or 60)
        overlaps = a['_dt'] < end_b and b['_dt'] < end_a
        if overlaps and a.get('room_id') and a['room_id'] == b.get('room_id'):
            conflict_ids.add(a['id']); conflict_ids.add(b['id'])
        if overlaps and a.get('instructor_id') and a['instructor_id'] == b.get('instructor_id'):
            conflict_ids.add(a['id']); conflict_ids.add(b['id'])
        sec_a = (a.get('section') or '').strip()
        sec_b = (b.get('section') or '').strip()
        if overlaps and sec_a and sec_a == sec_b:
            conflict_ids.add(a['id']); conflict_ids.add(b['id'])
        subj_a = (a.get('subject_name') or '').strip().lower()
        subj_b = (b.get('subject_name') or '').strip().lower()
        if subj_a and subj_a == subj_b and a['_dt'] != b['_dt']:
            conflict_ids.add(a['id']); conflict_ids.add(b['id'])

print('Found', len(conflict_ids), 'conflicts.')
unschedule_exams(list(conflict_ids))
print('Unscheduled.')

period_start, period_end = get_exam_period()
pending = get_pending_exams()
rooms = get_all_rooms()
instructors = get_active_instructors()
booked = get_already_scheduled_slots()
proctor_av = get_proctor_availability()
settings = get_system_settings()

print(f'Pending: {len(pending)}, Booked: {len(booked)}')

result = run_scheduler(
    pending_exams=pending,
    rooms=rooms,
    instructors=instructors,
    booked_slots=booked,
    period_start=period_start,
    period_end=period_end,
    proctor_availability=proctor_av,
    settings=settings
)

print('Scheduled:', len(result['scheduled']))
print('Failed:', len(result['failed']))
if result['failed']:
    print('First failure reason:', result['failed'][0]['reason'])
