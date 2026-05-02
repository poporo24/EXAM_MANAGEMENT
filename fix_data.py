from system.database import open_db

db = open_db()
if db:
    c = db.cursor()
    # Normalize empty/null status to 'Pending' and clear old stale assignments
    c.execute("""
        UPDATE exams 
        SET status = 'Pending', room_id = NULL, instructor_id = NULL, instructor_name = NULL 
        WHERE status = '' OR status IS NULL OR status NOT IN ('Pending','Scheduled','Unscheduled')
    """)
    db.commit()
    print(f"Fixed {c.rowcount} rows with bad status.")

    # Confirm current state
    c2 = db.cursor(dictionary=True)
    c2.execute("SELECT id, subject_name, exam_date_time, duration_minutes, status FROM exams")
    rows = c2.fetchall()
    for r in rows:
        print(r)
    db.close()
