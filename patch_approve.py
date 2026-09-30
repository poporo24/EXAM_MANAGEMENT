with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

old_approve = """def approve_student(user_id):
    \"\"\"Activate a student account and notify them.\"\"\"
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor.execute("UPDATE users SET is_active=1 WHERE id=%s AND role='student'", (user_id,))
        db.commit()
        # Notify the student
        cursor_r.execute("SELECT full_name FROM users WHERE id=%s", (user_id,))
        row = cursor_r.fetchone()
        name = row['full_name'] if row else 'Student'
        create_notification(
            user_id,
            "o. Account Approved",
            f"Hi {name}! Your student account has been approved by the administrator. "
            "You can now log in and view your exam timetable."
        )
        return True
    finally:
        db.close()"""

new_approve = """def approve_student(user_id):
    \"\"\"Activate a student/proctor account and notify them.\"\"\"
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        # Update for both students and proctors
        cursor.execute("UPDATE users SET is_active=1 WHERE id=%s AND role IN ('student', 'proctor')", (user_id,))
        db.commit()
        
        # Notify via in-app and Email
        cursor_r.execute("SELECT full_name, email, role FROM users WHERE id=%s", (user_id,))
        row = cursor_r.fetchone()
        if not row:
            return True
            
        name = row['full_name']
        email = row['email']
        role = row['role']
        
        if role == 'student':
            title = "o. Account Approved"
            msg = (f"Hi {name}! Your student account has been approved by the administrator. "
                   "You can now log in and view your exam timetable.")
            email_subj = "Account Approved - Exam Timetable Available"
            email_body = (f"Dear {name},\n\n"
                          "Your account has been approved by the administrator. "
                          "Your exam timetable is now available on the system.\n\n"
                          "Please log in to the CCA Exam Management System to view your schedule.\n\n"
                          "Best,\nCCA Exam Management System")
        else:
            title = "o. Proctor Account Approved"
            msg = (f"Hi {name}! Your proctor account has been approved by the administrator. "
                   "You can now log in and view your proctoring schedule.")
            email_subj = "Account Approved - Proctoring Schedule Available"
            email_body = (f"Dear {name},\n\n"
                          "Your proctor account has been approved by the administrator. "
                          "Your assigned proctoring schedule is now available on the system.\n\n"
                          "Please log in to the CCA Exam Management System to view your assignments and set your availability.\n\n"
                          "Best,\nCCA Exam Management System")
            
        create_notification(user_id, title, msg)
        
        # Send Email
        from app import send_email_notification
        send_email_notification(email, email_subj, email_body)
        
        return True
    finally:
        db.close()"""

if old_approve in db:
    db = db.replace(old_approve, new_approve)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Patched approve_student")
else:
    print("Could not find old_approve")
