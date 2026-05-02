from system.database import open_db

db = open_db()
c = db.cursor()

print("=== ALTERING status ENUM to include Scheduled + Unscheduled ===")
c.execute("""
    ALTER TABLE exams 
    MODIFY COLUMN status 
    ENUM('Pending','Ongoing','Completed','Scheduled','Unscheduled') 
    DEFAULT 'Pending'
""")
db.commit()
print("ALTER done.")

# Now fix current rows that have empty status (caused by the failed ENUM insert)
# BUSCOM and KAPCUL already have room_id/instructor_id set — mark them Scheduled
c.execute("""
    UPDATE exams 
    SET status = 'Scheduled'
    WHERE room_id IS NOT NULL 
      AND instructor_id IS NOT NULL 
      AND (status = '' OR status IS NULL)
""")
db.commit()
print(f"Re-applied Scheduled to {c.rowcount} rows.")

# Normalize any remaining blanks back to Pending
c.execute("UPDATE exams SET status = 'Pending' WHERE status = '' OR status IS NULL")
db.commit()
print(f"Reset {c.rowcount} remaining blank-status rows to Pending.")

# Confirm final state
c.execute("SELECT id, subject_name, room_id, instructor_id, instructor_name, status FROM exams")
print("\n=== FINAL EXAM DATA ===")
for r in c.fetchall():
    print(r)

c.execute("SHOW COLUMNS FROM exams LIKE 'status'")
print("\n=== STATUS COLUMN DEFINITION ===")
print(c.fetchone())

db.close()
print("\nDone! The system is ready.")
