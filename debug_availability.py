"""
debug_availability.py - Test what the scheduler actually sees
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from system.database import open_db, get_proctor_availability, get_all_instructors

print("=" * 60)
print("DEBUG: Proctor Availability Data")
print("=" * 60)

# 1. Show all instructors
instructors = get_all_instructors()
print(f"\nInstructors ({len(instructors)}):")
for inst in instructors:
    print(f"  ID={inst['id']}  Name={inst['name']}  Dept={inst.get('department','')}")

# 2. Show raw DB data
db = open_db()
if db:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proctor_availability ORDER BY instructor_id, available_date")
    rows = cursor.fetchall()
    print(f"\nRaw proctor_availability table ({len(rows)} rows):")
    for r in rows:
        print(f"  instructor_id={r['instructor_id']}  date={r['available_date']} "
              f"(type={type(r['available_date']).__name__})  "
              f"start={r.get('start_time')} (type={type(r.get('start_time')).__name__})  "
              f"end={r.get('end_time')} (type={type(r.get('end_time')).__name__})")
    db.close()

# 3. Show what get_proctor_availability() returns
avail = get_proctor_availability()
print(f"\nget_proctor_availability() returns ({len(avail)} instructors with entries):")
for iid, entries in avail.items():
    print(f"  Instructor ID={iid}:")
    for e in entries:
        print(f"    date={e['date']} (type={type(e['date']).__name__})  "
              f"start={e['start_time']} (type={type(e['start_time']).__name__})  "
              f"end={e['end_time']} (type={type(e['end_time']).__name__})")

# 4. Simulate what the scheduler does
print("\n" + "=" * 60)
print("SIMULATION: inst_available() checks")
print("=" * 60)
from datetime import datetime, time as dt_time, timedelta

# Simulate a few exam slots
test_dates_str = []
if avail:
    # Use dates from actual availability
    for iid, entries in avail.items():
        for e in entries:
            test_dates_str.append(str(e['date']))
        break

if not test_dates_str:
    print("\nNo availability entries found -- nothing to test.")
    print("The scheduler treats ALL proctors as available everywhere.")
else:
    from datetime import date as dt_date
    for iid in avail:
        inst_name = next((i['name'] for i in instructors if i['id'] == iid), f"ID {iid}")
        print(f"\nInstructor: {inst_name} (ID={iid})")
        avail_entries = avail[iid]

        # Test every hour on their available date AND a non-available date
        test_date = avail_entries[0]['date']
        non_avail_date = test_date + timedelta(days=1)

        for test_d in [test_date, non_avail_date]:
            print(f"\n  Date: {test_d} ({'AVAILABLE' if test_d == test_date else 'NOT AVAILABLE'} date)")
            for hour in [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
                start_dt = datetime.combine(test_d, dt_time(hour, 0))
                end_dt = start_dt + timedelta(minutes=60)

                # Replicate inst_available logic
                exam_date = start_dt.date()
                exam_start_time = start_dt.time()
                exam_end_time = end_dt.time()

                found = False
                for entry in avail_entries:
                    entry_date = entry['date']
                    if hasattr(entry_date, 'date'):
                        entry_date = entry_date.date()
                    if entry_date != exam_date:
                        continue
                    avail_start = entry.get('start_time', dt_time(7, 0))
                    avail_end = entry.get('end_time', dt_time(20, 0))
                    if isinstance(avail_start, timedelta):
                        avail_start = (datetime.min + avail_start).time()
                    if isinstance(avail_end, timedelta):
                        avail_end = (datetime.min + avail_end).time()
                    if exam_start_time >= avail_start and exam_end_time <= avail_end:
                        found = True
                        break

                status = "ALLOWED" if found else "BLOCKED"
                print(f"    {hour:02d}:00-{hour+1:02d}:00  -> {status}")

print("\n[DONE]")
