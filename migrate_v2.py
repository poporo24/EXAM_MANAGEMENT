from system.database import open_db

db = open_db()
c = db.cursor()

print("=== 1. Add subject_type to exams ===")
c.execute("SHOW COLUMNS FROM exams LIKE 'subject_type'")
if c.fetchone():
    print("Already exists.")
else:
    c.execute("ALTER TABLE exams ADD COLUMN subject_type ENUM('Major','Minor') NOT NULL DEFAULT 'Major' AFTER section")
    db.commit()
    print("Done.")

print("=== 2. Make exam_date_time nullable ===")
c.execute("ALTER TABLE exams MODIFY COLUMN exam_date_time DATETIME NULL")
db.commit()
print("Done.")

print("=== 3. Create proctor_availability ===")
c.execute("""
    CREATE TABLE IF NOT EXISTS proctor_availability (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        instructor_id INT NOT NULL,
        available_date DATE NOT NULL,
        start_time    TIME NOT NULL DEFAULT '07:00:00',
        end_time      TIME NOT NULL DEFAULT '20:00:00',
        UNIQUE KEY uq_proctor_date (instructor_id, available_date),
        FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
    )
""")
db.commit()
print("Done.")

print("=== 4. Reset existing exams to Pending + clear date/time ===")
c.execute("""UPDATE exams SET status='Pending', exam_date_time=NULL,
              room_id=NULL, instructor_id=NULL, instructor_name=NULL
           WHERE 1=1""")
db.commit()
print(f"Reset {c.rowcount} exams.")

print("\n=== Final schema ===")
c.execute("SHOW COLUMNS FROM exams")
for col in c.fetchall():
    print(col)

db.close()
print("\nMigration complete!")
