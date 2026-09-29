"""
seed_real_data.py
Imports real exam schedule data into the CCA Exam Management System.
Exam period: August 24-29, 2026  (original Thursday → August 27, 2026)
Run: python seed_real_data.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, date
from system.database import open_db

# ── Raw schedule data ────────────────────────────────────────────────────────
# (day, start_time, end_time, duration_hrs, room, subject, section, proctor, institute, num_students)
RAW = [
    ("Thursday", "08:00", "09:00", 60, "P104", "EXPTPSY",       "PSYCH 201", "Babadilla, Roan",                None,     10),
    ("Thursday", "08:00", "09:00", 60, "P105", "EXPTPSY",       "PSYCH 202", "Andes, Arbien Paulo E.",          None,      4),
    ("Thursday", "08:00", "09:00", 60, "P203", "EXPTPSY",       "PSYCH 203", "Dapiton, Ethelberth P.",          None,      7),
    ("Thursday", "08:00", "09:00", 60, "P204", "EXPTPSY",       "PSYCH 204", "Malit, Ronaldo",                  None,     11),
    ("Thursday", "08:00", "09:00", 60, "P301", "EXPTPSY",       "PSYCH 205", "Mejares, Novie Joy G.",            None,      3),
    ("Thursday", "08:00", "09:00", 60, "P302", "IBT",           "E401",      "dela Cruz, Ruth",                 None,      3),
    ("Thursday", "08:00", "09:00", 60, "P303", "IBT",           "E402",      "Punsalan, Beverly Shayne G.",     None,      8),
    ("Thursday", "08:00", "09:00", 60, "P304", "IBT",           "E403",      "Tongol, Florabel",                None,     10),
    ("Thursday", "08:00", "09:00", 60, "P305", "IBT",           "E404",      "Halili, Ronie S.",                None,      6),
    ("Thursday", "08:00", "09:00", 60, "P401", "IBT",           "E405",      "Diaz, Francis F.",                None,      3),
    ("Thursday", "08:00", "09:00", 60, "P402", "PE 110",        "BPE 201",   "Magarro, Margeree Grace P.",      None,      4),
    ("Thursday", "08:00", "09:00", 60, "P403", "MATH 2",        "BPE 202",   "Gaviola, Maria Leonor",           None,      3),
    ("Thursday", "08:00", "09:00", 60, "P404", "MATH 2",        "BSNE 201",  "Zapata, Jannette",               None,      4),
    ("Thursday", "08:00", "09:00", 60, "P405", "MATH 112",      "M 301",     "Franco, Marcus Emile C.",         None,      4),
    ("Thursday", "08:00", "10:00", 120,"L401", "8MAEL1",        "C101",      "Fabian, Brandon",                 "ICSLIS",  6),
    ("Thursday", "08:00", "10:00", 120,"L402", "8MAEL1",        "C102",      "Acampado, Elizabeth M.",          "ICSLIS",  4),
    ("Thursday", "08:00", "10:00", 120,"L403", "8MAEL1",        "C103",      "Palma, Reinel C.",                "ICSLIS",  4),
    ("Thursday", "08:00", "10:00", 120,"L404", "8MAEL1",        "C104",      "Requiez, Rejy Joash",             "ICSLIS",  5),
    ("Thursday", "08:00", "09:00", 60, "L405", "FILIPINO 2",    "BSNE 301",  "Pillas, Mark Lester L.",          None,      4),
    ("Thursday", "08:00", "09:00", 60, "L406", "TOURCULDIV",    "T301",      "Carlos, Caren A.",                None,      5),
    ("Thursday", "08:00", "09:00", 60, "L407", "TOURCULDIV",    "T302",      "Vinuya, Jerome",                  None,      4),
    ("Thursday", "08:00", "09:00", 60, "L408", "TOURCULDIV",    "T303",      "Legaspi, Jul Newton A.",          None,      5),
    ("Thursday", "08:00", "09:00", 60, "L409", "TOURCULDIV",    "T304",      "Tinio, Justine John L.",          None,      5),
    ("Thursday", "08:00", "09:00", 60, "L410", "TOURCULDIV",    "T305",      "Fernando, Leanjo R.",             None,      3),
    ("Thursday", "08:00", "09:00", 60, "R401", "TOURCULDIV",    "T306",      "San Pedro, Abraham L.",           None,      3),
    ("Thursday", "08:00", "09:00", 60, "R402", "TOURCULDIV",    "T307",      "Ibasco, Florenda",                None,      4),
    ("Thursday", "09:00", "10:00", 60, "P104", "INTROCOUN",     "PSYCH 201", "Babadilla, Roan",                None,     10),
    ("Thursday", "09:00", "10:00", 60, "P105", "INTROCOUN",     "PSYCH 202", "Mohamad, Jevin Jade P",          None,      6),
    ("Thursday", "09:00", "10:00", 60, "P203", "INTROCOUN",     "PSYCH 203", "Dapiton, Ethelberth P.",          None,      7),
    ("Thursday", "09:00", "10:00", 60, "P204", "INTROCOUN",     "PSYCH 204", "Malit, Ronaldo",                  None,     11),
    ("Thursday", "09:00", "10:00", 60, "P301", "INTROCOUN",     "PSYCH 205", "Carreon, Kiara Marie C.",         None,      5),
    ("Thursday", "09:00", "10:00", 60, "P302", "PE 108",        "BPE 201",   "dela Cruz, Ruth",                 None,      3),
    ("Thursday", "09:00", "10:00", 60, "P303", "PE 108",        "BPE 202",   "Punsalan, Beverly Shayne G.",     None,      8),
    ("Thursday", "09:00", "10:00", 60, "P304", "ENG 2",         "BSNE 201",  "Tongol, Florabel",                None,     10),
    ("Thursday", "09:00", "10:00", 60, "P401", "LIS 04",        "L201",      "Seng, Olga G.",                   "ICSLIS",  3),
    ("Thursday", "09:00", "10:00", 60, "P405", "MATH 113",      "M 301",     "Torres, Enrique III R.",          None,      5),
    ("Thursday", "09:00", "10:00", 60, "L405", "PROFED PCK 6",  "BSNE 301",  "San Pedro, Abraham L.",           None,      3),
]

# Date mapping: Thursday in the Aug 24-29, 2026 week = August 27, 2026
DAY_MAP = {"Thursday": date(2026, 8, 27)}

# ─────────────────────────────────────────────────────────────────────────────

db = open_db()
if not db:
    print("ERROR: Cannot connect to MySQL.")
    sys.exit(1)
c = db.cursor(dictionary=True)

print("=" * 60)
print("CCA Exam Management — Seeding Real Schedule Data")
print("Exam period: August 24-29, 2026")
print("=" * 60)

# ── 1. Upsert rooms ───────────────────────────────────────────────────────────
print("\n[1] Inserting rooms...")
rooms_seen = {}
for row in RAW:
    room_name = row[4]
    if room_name not in rooms_seen:
        rooms_seen[room_name] = True
        c.execute("SELECT id FROM rooms WHERE room_name = %s", (room_name,))
        r = c.fetchone()
        if not r:
            c.execute("INSERT INTO rooms (room_name, capacity) VALUES (%s, %s)", (room_name, 50))
            print(f"   [+] Room {room_name}")
        else:
            print(f"   [~] Room {room_name} already exists")

db.commit()

# Build room lookup
c.execute("SELECT id, room_name FROM rooms")
room_map = {r['room_name']: r['id'] for r in c.fetchall()}

# ── 2. Upsert instructors ─────────────────────────────────────────────────────
print("\n[2] Inserting instructors...")
inst_seen = {}
for row in RAW:
    name = row[7]
    if name and name not in inst_seen:
        inst_seen[name] = True
        c.execute("SELECT id FROM instructors WHERE name = %s", (name,))
        r = c.fetchone()
        if not r:
            c.execute("INSERT INTO instructors (name, status) VALUES (%s, 'Active')", (name,))
            print(f"   [+] {name}")
        else:
            print(f"   [~] {name}")

db.commit()

# Build instructor lookup
c.execute("SELECT id, name FROM instructors")
inst_map = {r['name']: r['id'] for r in c.fetchall()}

# ── 3. Get institute IDs ───────────────────────────────────────────────────────
c.execute("SELECT id, code FROM institutes")
institute_map = {r['code']: r['id'] for r in c.fetchall()}

# ── 4. Clear existing scheduled exams for this period ─────────────────────────
print("\n[3] Clearing any existing exams for Aug 24-29, 2026...")
c.execute("""
    DELETE FROM exams
    WHERE exam_date_time >= '2026-08-24 00:00:00'
      AND exam_date_time <= '2026-08-29 23:59:59'
""")
print(f"   Cleared {c.rowcount} existing rows.")
db.commit()

# ── 5. Insert exams directly as Scheduled ─────────────────────────────────────
print("\n[4] Inserting scheduled exams...")
inserted = 0
for row in RAW:
    day_name, start_str, end_str, dur_min, room_name, subject, section, proctor_name, inst_code, num_students = row

    exam_date = DAY_MAP.get(day_name)
    if not exam_date:
        print(f"   [!] Unknown day: {day_name}, skipping")
        continue

    # Parse start time
    h, m = map(int, start_str.split(":"))
    exam_dt = datetime(exam_date.year, exam_date.month, exam_date.day, h, m)

    room_id     = room_map.get(room_name)
    proctor_id  = inst_map.get(proctor_name)
    inst_id     = institute_map.get(inst_code) if inst_code else None

    if not room_id:
        print(f"   [!] Room not found: {room_name}")
        continue
    if not proctor_id:
        print(f"   [!] Proctor not found: {proctor_name}")
        continue

    # Determine subject_type from section pattern:
    # Lab rooms (L*) or 2-hour exams = Minor; standard 1-hour = Major
    subject_type = "Minor" if dur_min >= 120 else "Major"

    c.execute("""
        INSERT INTO exams
            (subject_name, section, subject_type, duration_minutes,
             room_id, instructor_id, institute_id,
             exam_date_time, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Scheduled')
    """, (subject, section, subject_type, dur_min,
          room_id, proctor_id, inst_id,
          exam_dt))
    inserted += 1

db.commit()
print(f"\n   ✅ Inserted {inserted} scheduled exams.")

# ── 6. Save exam period settings ──────────────────────────────────────────────
print("\n[5] Saving exam period (Aug 24-29, 2026)...")
c.execute("SELECT id FROM exam_settings LIMIT 1")
row_es = c.fetchone()
if row_es:
    c.execute("""
        UPDATE exam_settings
        SET period_start = '2026-08-24', period_end = '2026-08-29'
        WHERE id = %s
    """, (row_es['id'],))
else:
    c.execute("""
        INSERT INTO exam_settings (period_start, period_end)
        VALUES ('2026-08-24', '2026-08-29')
    """)
db.commit()
print("   ✅ Period saved.")

# ── 7. Summary ────────────────────────────────────────────────────────────────
c.execute("SELECT COUNT(*) AS n FROM rooms")
n_rooms = c.fetchone()['n']
c.execute("SELECT COUNT(*) AS n FROM instructors")
n_inst = c.fetchone()['n']
c.execute("SELECT COUNT(*) AS n FROM exams WHERE status='Scheduled'")
n_exams = c.fetchone()['n']

db.close()

print("\n" + "=" * 60)
print(f"[DONE] Seed complete.")
print(f"  Rooms       : {n_rooms}")
print(f"  Instructors : {n_inst}")
print(f"  Exams       : {n_exams} scheduled")
print(f"  Period      : Aug 24 – Aug 29, 2026 (Thu slots on Aug 27)")
print("=" * 60)
print("\nOpen http://127.0.0.1:9999/schedule to view the timetable.")
