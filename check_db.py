from system.database import open_db

db = open_db()
c = db.cursor()

# Check column definition
c.execute("SHOW COLUMNS FROM exams")
print("=== EXAMS TABLE COLUMNS ===")
for col in c.fetchall():
    print(col)

print()
# Check current data
c.execute("SELECT id, subject_name, room_id, instructor_id, instructor_name, status FROM exams")
print("=== CURRENT EXAM DATA ===")
for r in c.fetchall():
    print(r)

db.close()
