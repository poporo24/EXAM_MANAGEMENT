from system.database import open_db

db = open_db()
c = db.cursor()

print("=== Adding 'section' column to exams ===")
c.execute("SHOW COLUMNS FROM exams LIKE 'section'")
if c.fetchone():
    print("Column already exists, skipping.")
else:
    c.execute("ALTER TABLE exams ADD COLUMN section VARCHAR(50) NULL AFTER subject_name")
    db.commit()
    print("Done — 'section' column added.")

print("\n=== Current exams columns ===")
c.execute("SHOW COLUMNS FROM exams")
for col in c.fetchall():
    print(col)

db.close()
