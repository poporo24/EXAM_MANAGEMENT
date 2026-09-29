import sys
sys.path.append('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT')
from system.database import open_db

db = open_db()
cursor = db.cursor(dictionary=True)

# Find duplicates by subject_name and section
cursor.execute("SELECT id, subject_name, section FROM exams ORDER BY id ASC")
all_exams = cursor.fetchall()

seen = set()
to_delete = []

for e in all_exams:
    key = (e['subject_name'].strip().lower(), (e['section'] or '').strip().lower())
    if key in seen:
        to_delete.append(e['id'])
    else:
        seen.add(key)

print(f"Found {len(to_delete)} duplicate exams.")

if to_delete:
    format_strings = ','.join(['%s'] * len(to_delete))
    cursor.execute(f"DELETE FROM exams WHERE id IN ({format_strings})", tuple(to_delete))
    db.commit()
    print("Deleted duplicates.")
else:
    print("No duplicates found.")
