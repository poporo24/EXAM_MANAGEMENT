from datetime import date
from collections import defaultdict
from system.scheduler import run_scheduler

# Simulate exams including None section/subject_type (like existing DB rows)
pending = [
    {'id': 1, 'subject_name': 'BUSCOM',  'section': 'BSIS-301', 'subject_type': 'Major', 'duration_minutes': 60},
    {'id': 2, 'subject_name': 'KAPCUL',  'section': 'BSIS-301', 'subject_type': 'Major', 'duration_minutes': 60},
    {'id': 3, 'subject_name': 'ARTAPP',  'section': 'BSIS-301', 'subject_type': 'Major', 'duration_minutes': 60},
    {'id': 4, 'subject_name': 'MATH101', 'section': None,        'subject_type': None,    'duration_minutes': 60},
    {'id': 5, 'subject_name': 'PE',      'section': 'BSIS-302', 'subject_type': 'Minor', 'duration_minutes': 60},
]
rooms = [
    {'id': 1, 'room_name': 'R202', 'capacity': 40},
    {'id': 2, 'room_name': 'R203', 'capacity': 40},
]
instructors = [
    {'id': 1, 'name': 'Clark Soysoy'},
    {'id': 2, 'name': 'Izzy Kabuktut'},
]

result = run_scheduler(
    pending_exams=pending,
    rooms=rooms,
    instructors=instructors,
    booked_slots=[],
    period_start=date(2026, 5, 5),
    period_end=date(2026, 5, 10),
    proctor_availability={}
)

print(f"Scheduled: {len(result['scheduled'])}")
print(f"Failed:    {len(result['failed'])}")

for s in result['scheduled']:
    exam = next(e for e in pending if e['id'] == s['exam_id'])
    print(f"  [{exam['subject_type'] or 'N/A':5}] {exam['subject_name']:10} sec={exam['section'] or '-':10} -> {s['exam_date_time']} Room:{s['room_id']} Proctor:{s['instructor_name']}")

for f in result['failed']:
    print(f"  FAILED Exam {f['exam_id']}: {f['reason']}")

# Verify max-2-major constraint for BSIS-301
day_major = defaultdict(int)
for s in result['scheduled']:
    exam = next(e for e in pending if e['id'] == s['exam_id'])
    if (exam.get('subject_type') or '') == 'Major' and (exam.get('section') or '') == 'BSIS-301':
        day_major[s['exam_date_time'].date()] += 1

print("\nMajor exams per day for BSIS-301:", dict(day_major))

violations = [d for d, cnt in day_major.items() if cnt > 2]
if violations:
    print(f"CONSTRAINT VIOLATED on: {violations}")
else:
    print("All constraints satisfied!")
