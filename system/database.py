import mysql.connector
from datetime import datetime, timedelta

def open_db():
    import os
    import mysql.connector
    
    # Check if we are on Render (using Aiven remote DB)
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # Connect using the remote URL (mysql://user:pass@host:port/dbname)
        import urllib.parse
        url = urllib.parse.urlparse(db_url)
        try:
            return mysql.connector.connect(
                host=url.hostname,
                user=url.username,
                password=url.password,
                database=url.path[1:], # remove leading slash
                port=url.port or 3306
            )
        except mysql.connector.Error as err:
            print(f"Remote DB Error: {err}")
            return None
    else:
        # Local XAMPP connection
        try:
            return mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="cca_exam_management_db"
            )
        except mysql.connector.Error as err:
            print(f"Local DB Error: {err}")
            return None

def get_system_settings():
    db = open_db()
    if not db:
        return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM system_settings WHERE id = 1")
        row = cursor.fetchone()
        return row if row else {}
    finally:
        db.close()

def save_system_settings(day_start, day_end, slot_interval_min, max_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs=2.0, minor_duration_hrs=1.0):
    db = open_db()
    if not db:
        return
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO system_settings (id, day_start, day_end, slot_interval_min, max_consecutive_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs, minor_duration_hrs)
            VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            day_start=VALUES(day_start), day_end=VALUES(day_end), slot_interval_min=VALUES(slot_interval_min), max_consecutive_proctor_hrs=VALUES(max_consecutive_proctor_hrs), travel_buffer_min=VALUES(travel_buffer_min), smtp_host=VALUES(smtp_host), smtp_port=VALUES(smtp_port), smtp_user=VALUES(smtp_user), smtp_password=VALUES(smtp_password), smtp_from=VALUES(smtp_from), smtp_use_tls=VALUES(smtp_use_tls), major_duration_hrs=VALUES(major_duration_hrs), minor_duration_hrs=VALUES(minor_duration_hrs)
        """, (day_start, day_end, slot_interval_min, max_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs, minor_duration_hrs))
        db.commit()
    finally:
        db.close()

# ── INSTITUTES ─────────────────────────────────────────────────────────────

def get_all_institutes():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM institutes ORDER BY name")
        return cursor.fetchall()
    finally:
        db.close()

def add_institute(name, code, capacity_default):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO institutes (name, code, capacity_default) VALUES (%s, %s, %s)", (name, code, capacity_default))
        db.commit()
    finally:
        db.close()

def edit_institute(id, name, code, capacity_default):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE institutes SET name=%s, code=%s, capacity_default=%s WHERE id=%s", (name, code, capacity_default, id))
        db.commit()
    finally:
        db.close()

def delete_institute(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor(dictionary=True)
        # check constraints
        cursor.execute("SELECT count(*) as c FROM rooms WHERE institute_id=%s", (id,))
        if cursor.fetchone()['c'] > 0: return "Cannot delete: Rooms depend on this institute."
        cursor.execute("SELECT count(*) as c FROM instructors WHERE institute_id=%s", (id,))
        if cursor.fetchone()['c'] > 0: return "Cannot delete: Instructors depend on this institute."
        cursor.execute("SELECT count(*) as c FROM exams WHERE institute_id=%s", (id,))
        if cursor.fetchone()['c'] > 0: return "Cannot delete: Exams depend on this institute."
        cursor.execute("DELETE FROM institutes WHERE id=%s", (id,))
        db.commit()
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()

# ── SUBJECTS ─────────────────────────────────────────────────────────────

def get_all_subjects():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT s.*, i.name as institute_name FROM subjects s LEFT JOIN institutes i ON s.institute_id = i.id ORDER BY s.name")
        return cursor.fetchall()
    finally:
        db.close()

def get_subjects_by_institute(institute_id):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM subjects WHERE institute_id=%s ORDER BY name", (institute_id,))
        return cursor.fetchall()
    finally:
        db.close()

def add_subject(name, code, institute_id, is_common, content_group_id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO subjects (name, code, institute_id, is_common, content_group_id) VALUES (%s, %s, %s, %s, %s)", (name, code, institute_id, is_common, content_group_id))
        db.commit()
    finally:
        db.close()

def edit_subject(id, name, code, institute_id, is_common, content_group_id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE subjects SET name=%s, code=%s, institute_id=%s, is_common=%s, content_group_id=%s WHERE id=%s", (name, code, institute_id, is_common, content_group_id, id))
        db.commit()
    finally:
        db.close()

def delete_subject(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT count(*) as c FROM exams WHERE subject_id=%s", (id,))
        if cursor.fetchone()['c'] > 0: return "Cannot delete: Exams depend on this subject."
        cursor.execute("DELETE FROM subjects WHERE id=%s", (id,))
        db.commit()
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()

def link_subjects_content_group(subject_id_a, subject_id_b):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT content_group_id FROM subjects WHERE id=%s", (subject_id_a,))
        cg_a = cursor.fetchone()['content_group_id']
        cursor.execute("SELECT content_group_id FROM subjects WHERE id=%s", (subject_id_b,))
        cg_b = cursor.fetchone()['content_group_id']
        
        if not cg_a and not cg_b:
            new_id = min(subject_id_a, subject_id_b)
            cursor.execute("UPDATE subjects SET content_group_id=%s WHERE id IN (%s, %s)", (new_id, subject_id_a, subject_id_b))
        elif cg_a and not cg_b:
            cursor.execute("UPDATE subjects SET content_group_id=%s WHERE id=%s", (cg_a, subject_id_b))
        elif cg_b and not cg_a:
            cursor.execute("UPDATE subjects SET content_group_id=%s WHERE id=%s", (cg_b, subject_id_a))
        else:
            cursor.execute("UPDATE subjects SET content_group_id=%s WHERE content_group_id=%s", (cg_a, cg_b))
        db.commit()
    finally:
        db.close()

def unlink_subject_content_group(subject_id):
    """Remove a subject from its content group. If only one subject remains in the
    group afterwards, dissolve the group by clearing that subject's group ID too."""
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor(dictionary=True)
        # Find the current group ID of this subject
        cursor.execute("SELECT content_group_id FROM subjects WHERE id=%s", (subject_id,))
        row = cursor.fetchone()
        if not row or not row['content_group_id']:
            return  # Not in a group, nothing to do
        cg_id = row['content_group_id']
        # Unlink this subject
        cursor.execute("UPDATE subjects SET content_group_id=NULL WHERE id=%s", (subject_id,))
        # Count remaining members of the group
        cursor.execute("SELECT id FROM subjects WHERE content_group_id=%s", (cg_id,))
        remaining = cursor.fetchall()
        # If only one subject is left alone in the group, dissolve the group
        if len(remaining) == 1:
            cursor.execute("UPDATE subjects SET content_group_id=NULL WHERE id=%s", (remaining[0]['id'],))
        db.commit()
    finally:
        db.close()

def get_common_subjects():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM subjects WHERE is_common=1 ORDER BY name")
        return cursor.fetchall()
    finally:
        db.close()

def get_subject_content_groups():
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM subjects WHERE content_group_id IS NOT NULL")
        rows = cursor.fetchall()
        groups = {}
        for r in rows:
            cg_id = r['content_group_id']
            if cg_id not in groups: groups[cg_id] = []
            groups[cg_id].append(r)
        return groups
    finally:
        db.close()

# ── USER MANAGEMENT ─────────────────────────────────────────────────────────────

def register_user(full_name, email, password, role, section=None, institute_id=None):
    from system.logic import hash_password
    db = open_db()
    if not db: return 'error'
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone(): return 'email_taken'
        hashed = hash_password(password)
        # Students and Proctors start inactive (pending admin approval)
        is_active = 0 if role in ('student', 'proctor') else 1
        
        instructor_id = None
        if role == 'proctor':
            cursor.execute("INSERT INTO instructors (name, status, institute_id, is_pwd, subjects_taught) VALUES (%s, 'Active', %s, 0, '')", (full_name, institute_id))
            instructor_id = cursor.lastrowid
            
        cursor.execute(
            "INSERT INTO users (full_name, email, password, role, section, institute_id, is_active, instructor_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (full_name, email, hashed, role, section, institute_id, is_active, instructor_id)
        )
        new_user_id = cursor.lastrowid
        db.commit()

        # Notify all admins about a new student/proctor registration awaiting approval
        if role in ('student', 'proctor'):
            cursor_r = db.cursor(dictionary=True)
            cursor_r.execute("SELECT id FROM users WHERE role IN ('admin') AND is_active=1")
            for admin in cursor_r.fetchall():
                create_notification(
                    admin['id'],
                    "🆕 New Student Registration",
                    f"{full_name} ({email}) has registered"
                    + (f" — Section: {section}" if section else "")
                    + ". Please review and approve their account in the Users panel."
                )

        return 'ok'
    except Exception as e:
        print(e)
        return 'error'
    finally:
        db.close()

def get_all_users():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, role, section, institute_id, is_super_admin FROM users ORDER BY full_name")
        return cursor.fetchall()
    finally:
        db.close()

def get_user_by_id(id):
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, role, section, institute_id, is_super_admin FROM users WHERE id=%s", (id,))
        return cursor.fetchone() or {}
    finally:
        db.close()

def update_user(id, full_name, email, role, section, institute_id, is_super_admin):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor(dictionary=True)
        # Check current role and instructor_id
        cursor.execute("SELECT role, instructor_id FROM users WHERE id=%s", (id,))
        user = cursor.fetchone()
        
        instructor_id = user.get('instructor_id') if user else None
        
        # If changing to proctor and doesn't have instructor_id, create one
        if role == 'proctor' and not instructor_id:
            cursor.execute("INSERT INTO instructors (name, status, institute_id, is_pwd, subjects_taught) VALUES (%s, 'Active', %s, 0, '')", (full_name, institute_id))
            instructor_id = cursor.lastrowid
            
        cursor.execute("UPDATE users SET full_name=%s, email=%s, role=%s, section=%s, institute_id=%s, is_super_admin=%s, instructor_id=%s WHERE id=%s",
                       (full_name, email, role, section, institute_id, is_super_admin, instructor_id, id))
        db.commit()
    finally:
        db.close()

def delete_user(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT email FROM users WHERE id=%s", (id,))
        user = cursor.fetchone()
        if not user:
            return "User not found"
        email = user['email']
        
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        db.commit()
        
        # Also delete from Firebase Auth so they can re-register if rejected
        try:
            from firebase_admin import auth as fb_auth
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.delete_user(fb_user.uid)
        except Exception:
            pass # Ignore if not found in Firebase
            
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()

def get_all_students():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role='student' ORDER BY full_name")
        return cursor.fetchall()
    finally:
        db.close()

def get_pending_users():
    """Return students who have registered but not yet been approved (is_active=0)."""
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, full_name, email, section, institute_id, created_at "
            "FROM users WHERE role IN ('student', 'proctor') AND is_active=0 ORDER BY created_at DESC"
        )
        return cursor.fetchall()
    finally:
        db.close()

def approve_student(user_id):
    """Activate a student/proctor account and notify them."""
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
            title = "Account Approved"
            msg = (f"Hi {name}! Your student account has been approved by the administrator. "
                   "You can now log in and view your exam timetable.")
            email_subj = "Account Approved - Exam Timetable Available"
            email_body = (f"Dear {name},\n\n"
                          "Your account has been approved by the administrator. "
                          "Your exam timetable is now available on the system.\n\n"
                          "Please log in to the CCA Exam Management System to view your schedule.\n\n"
                          "Best,\nCCA Exam Management System")
        else:
            title = "Proctor Account Approved"
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
        db.close()

def deactivate_student(user_id):
    """Deactivate a student account (is_active=0) and notify them."""
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor.execute("UPDATE users SET is_active=0 WHERE id=%s AND role='student'", (user_id,))
        db.commit()
        cursor_r.execute("SELECT full_name FROM users WHERE id=%s", (user_id,))
        row = cursor_r.fetchone()
        name = row['full_name'] if row else 'Student'
        create_notification(
            user_id,
            "⛔ Account Deactivated",
            f"Hi {name}, your student account has been deactivated by the administrator. "
            "Please contact the admin if you believe this is a mistake."
        )
        return True
    finally:
        db.close()

def bulk_deactivate_students(user_ids):
    """Deactivate multiple student accounts."""
    for uid in user_ids:
        deactivate_student(uid)

def bulk_delete_students(user_ids):
    """Delete multiple student accounts."""
    for uid in user_ids:
        delete_user(uid)

# ── ROOMS ──────────────────────────────────────────────────────────────────────

def get_all_rooms():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT r.*, i.name as institute_name FROM rooms r LEFT JOIN institutes i ON r.institute_id = i.id ORDER BY r.room_name")
        return cursor.fetchall()
    finally:
        db.close()

def get_rooms_by_institute(institute_id):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms WHERE institute_id=%s ORDER BY room_name", (institute_id,))
        return cursor.fetchall()
    finally:
        db.close()

def add_room(room_name, capacity, building=None, floor=1, institute_id=None, is_pwd_accessible=0):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO rooms (room_name, capacity, building, floor, institute_id, is_pwd_accessible) VALUES (%s, %s, %s, %s, %s, %s)",
                       (room_name, capacity, building, floor, institute_id, is_pwd_accessible))
        db.commit()
    finally:
        db.close()

def edit_room(id, room_name, capacity, building, floor, institute_id, is_pwd_accessible):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE rooms SET room_name=%s, capacity=%s, building=%s, floor=%s, institute_id=%s, is_pwd_accessible=%s WHERE id=%s",
                       (room_name, capacity, building, floor, institute_id, is_pwd_accessible, id))
        db.commit()
    finally:
        db.close()

def delete_room(id):
    db = open_db()
    if not db: return 'Database connection failed.'
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS cnt FROM exams WHERE room_id = %s", (id,))
        row = cursor.fetchone()
        if row and row['cnt'] > 0:
            return f"Cannot delete this room — it is assigned to {row['cnt']} exams."
        cursor.execute("DELETE FROM rooms WHERE id = %s", (id,))
        db.commit()
        return None
    except Exception as e:
        return f'Delete failed: {e}'
    finally:
        db.close()

def bulk_import_rooms(rows):
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                # Need to look up institute_id if institute_code is provided
                institute_id = None
                if 'institute_code' in row and row['institute_code']:
                    cursor.execute("SELECT id FROM institutes WHERE code=%s", (row['institute_code'],))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                cursor.execute("INSERT INTO rooms (room_name, capacity, building, floor, institute_id, is_pwd_accessible) VALUES (%s, %s, %s, %s, %s, %s)",
                               (row.get('room_name'), row.get('capacity'), row.get('building'), row.get('floor', 1), institute_id, row.get('pwd_accessible', 0)))
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
        db.commit()
    finally:
        db.close()
    return (success_count, error_list)

# ── INSTRUCTORS ────────────────────────────────────────────────────────────────

def get_all_instructors():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, u.email AS proctor_email, inst.name as institute_name,
                   (SELECT ROUND(COALESCE(SUM(duration_minutes)/60.0, 0), 1) FROM exams WHERE instructor_id = i.id AND status = 'Scheduled') as total_hours
            FROM instructors i
            LEFT JOIN users u ON u.instructor_id = i.id AND u.role = 'proctor'
            LEFT JOIN institutes inst ON i.institute_id = inst.id
            ORDER BY i.name ASC
        """)
        return cursor.fetchall()
    finally:
        db.close()

def get_active_instructors():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM instructors WHERE status='Active' ORDER BY name")
        return cursor.fetchall()
    finally:
        db.close()

def get_instructor_by_id(id):
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM instructors WHERE id=%s", (id,))
        return cursor.fetchone() or {}
    finally:
        db.close()

def add_instructor(name, institute_id=None, building=None, is_pwd=0, subjects_taught='', provided_email=''):
    from system.logic import hash_password
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO instructors (name, status, institute_id, building, is_pwd, subjects_taught) VALUES (%s, 'Active', %s, %s, %s, %s)",
                       (name, institute_id, building, is_pwd, subjects_taught))
        instructor_id = cursor.lastrowid

        import re
        proctor_email = provided_email.strip()
        
        def clean_email_name(n):
            # Convert to lowercase, replace non-alphanumeric with dot, and remove multiple dots
            cleaned = re.sub(r'[^a-z0-9]', '.', n.lower())
            return re.sub(r'\.+', '.', cleaned).strip('.')

        if not proctor_email:
            email_name = clean_email_name(name)
            proctor_email = f"{email_name}@cca.edu.ph"
            
        proctor_password = "proctor123"

        cursor.execute("SELECT id FROM users WHERE email = %s", (proctor_email,))
        if cursor.fetchone():
            email_name = clean_email_name(name)
            proctor_email = f"{email_name}.{instructor_id}@cca.edu.ph"

        hashed = hash_password(proctor_password)
        cursor.execute("INSERT INTO users (full_name, email, password, role, instructor_id) VALUES (%s, %s, %s, 'proctor', %s)",
                       (name, proctor_email, hashed, instructor_id))
        db.commit()
    finally:
        db.close()

def edit_instructor(id, name, institute_id, building, is_pwd, subjects_taught):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE instructors SET name=%s, institute_id=%s, building=%s, is_pwd=%s, subjects_taught=%s WHERE id=%s",
                       (name, institute_id, building, is_pwd, subjects_taught, id))
        db.commit()
    finally:
        db.close()

def deactivate_instructor(id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE instructors SET status='Inactive' WHERE id=%s", (id,))
        # Optional: deactivate linked user by scrambling password or setting flag if exists
        db.commit()
    finally:
        db.close()

def activate_instructor(id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE instructors SET status='Active' WHERE id=%s", (id,))
        db.commit()
    finally:
        db.close()

def delete_instructor(instructor_id):
    db = open_db()
    if not db: return 'Database connection failed.'
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS cnt FROM exams WHERE instructor_id = %s", (instructor_id,))
        row = cursor.fetchone()
        if row and row['cnt'] > 0:
            return f"Cannot delete this instructor — assigned to {row['cnt']} exams."
        cursor.execute("DELETE FROM instructors WHERE id = %s", (instructor_id,))
        db.commit()
        return None
    except Exception as e:
        return f'Delete failed: {e}'
    finally:
        db.close()

def bulk_import_instructors(rows):
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                institute_id = None
                if 'institute_code' in row and row['institute_code']:
                    cursor.execute("SELECT id FROM institutes WHERE code=%s", (row['institute_code'],))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                add_instructor(row.get('name'), institute_id, row.get('building'), row.get('is_pwd', 0), row.get('subjects_taught', ''), provided_email=row.get('email', ''))
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
    finally:
        db.close()
    return (success_count, error_list)

def get_proctor_total_hours(instructor_id, date_from=None, date_to=None):
    db = open_db()
    if not db: return 0.0
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT SUM(duration_minutes) as tot FROM exams WHERE instructor_id=%s AND status='Scheduled'"
        params = [instructor_id]
        if date_from and date_to:
            query += " AND exam_date_time >= %s AND exam_date_time <= %s"
            params.extend([date_from, date_to])
        cursor.execute(query, tuple(params))
        res = cursor.fetchone()
        return float(res['tot'] or 0) / 60.0
    finally:
        db.close()

def get_all_proctor_hours_summary():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.id as instructor_id, i.name, COUNT(e.id) as exam_count, SUM(IFNULL(e.duration_minutes, 0))/60.0 as total_hours
            FROM instructors i
            LEFT JOIN exams e ON e.instructor_id = i.id AND e.status='Scheduled'
            GROUP BY i.id, i.name
        """)
        return cursor.fetchall()
    finally:
        db.close()

# ── EXAMS ──────────────────────────────────────────────────────────────────────

def add_exam(name, section, subject_type, duration_minutes, institute_id=None, subject_id=None):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        duration_minutes = int(duration_minutes) if duration_minutes else 60
        section = section.strip().upper() if section else None
        subject_type = subject_type if subject_type in ('Major', 'Minor') else 'Major'
        cursor.execute(
            """INSERT INTO exams (subject_name, section, subject_type, duration_minutes, status, institute_id, subject_id)
               VALUES (%s, %s, %s, %s, 'Pending', %s, %s)""",
            (name, section, subject_type, duration_minutes, institute_id, subject_id))
        db.commit()
    finally:
        db.close()

def edit_exam_details(id, name, section, subject_type, duration_minutes, institute_id, subject_id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute(
            """UPDATE exams SET subject_name=%s, section=%s, subject_type=%s, duration_minutes=%s, institute_id=%s, subject_id=%s WHERE id=%s""",
            (name, section, subject_type, duration_minutes, institute_id, subject_id, id))
        db.commit()
    finally:
        db.close()

def delete_exam(exam_id):
    db = open_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))
            db.commit()
        finally:
            db.close()

def delete_all_exams():
    """Delete every exam. Related relievers, exam_collection, and proctor_absence
    rows are removed automatically via ON DELETE CASCADE."""
    db = open_db()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM exams")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM exams")
        db.commit()
        return count
    finally:
        db.close()

def bulk_import_exams(rows):
    """Insert multiple exams from parsed CSV rows.
    Each row dict: subject_name, section, subject_type, institute_id (resolved).
    Duration is auto-set from system settings based on subject_type.
    Returns (success_count, error_list)."""
    db = open_db()
    if not db: return (0, ["DB Error"])
    # Load duration defaults from settings
    settings = get_system_settings()
    major_min = int(float(settings.get('major_duration_hrs', 2)) * 60)
    minor_min = int(float(settings.get('minor_duration_hrs', 1)) * 60)
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                subject_type = row.get('subject_type', 'Major')
                # Auto-set duration based on subject type
                if subject_type in ('Minor', 'Laboratory'):
                    dur_min = minor_min
                else:
                    dur_min = major_min
                cursor.execute(
                    """INSERT INTO exams (subject_name, section, subject_type, duration_minutes, status, institute_id, subject_id)
                       VALUES (%s, %s, %s, %s, \'Pending\', %s, %s)""",
                    (row.get('subject_name'), row.get('section') or None,
                     subject_type, dur_min,
                     row.get('institute_id')))
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
        db.commit()
    finally:
        db.close()
    return (success_count, error_list)

def bulk_delete_exams(exam_ids):
    """Delete a list of exam IDs. Returns (deleted_count, error_list)."""
    db = open_db()
    if not db: return (0, ["DB Error"])
    deleted, errors = 0, []
    try:
        cursor = db.cursor()
        for eid in exam_ids:
            try:
                cursor.execute("DELETE FROM exams WHERE id = %s", (int(eid),))
                deleted += 1
            except Exception as e:
                errors.append(str(e))
        db.commit()
    finally:
        db.close()
    return (deleted, errors)

def get_pending_exams():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, s.content_group_id
            FROM exams e
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.exam_date_time IS NULL OR e.status IN ('Pending', 'Unscheduled')
        """)
        return cursor.fetchall()
    finally:
        db.close()

def get_all_exams():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, i.name AS instructor_name, inst.name as institute_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            ORDER BY e.exam_date_time ASC, e.section ASC
        """)
        return cursor.fetchall()
    finally:
        db.close()

def get_exam_by_id(exam_id):
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, i.name AS instructor_name, inst.name as institute_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            WHERE e.id = %s
        """, (exam_id,))
        return cursor.fetchone() or {}
    finally:
        db.close()

def get_student_exam_load_per_day(section, institute_id=None):
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT DATE(exam_date_time) as d, COUNT(*) as c FROM exams WHERE section=%s AND status='Scheduled'"
        params = [section]
        if institute_id:
            query += " AND institute_id=%s"
            params.append(institute_id)
        query += " GROUP BY DATE(exam_date_time)"
        cursor.execute(query, tuple(params))
        res = cursor.fetchall()
        return {str(r['d']): r['c'] for r in res if r['d']}
    finally:
        db.close()

# ── SCHEDULER HELPERS (Existing + Enhanced) ──────────────────────────────

def get_dashboard_stats():
    db = open_db()
    if not db: return {}
    stats = {'total_exams': 0, 'rooms': 0, 'instructors': 0, 'scheduled': 0, 'pending': 0, 'by_institute': []}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as c FROM exams")
        stats['total_exams'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM rooms")
        stats['rooms'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM instructors")
        stats['instructors'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status = 'Scheduled'")
        stats['scheduled'] = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status = 'Pending' OR status = 'Unscheduled'")
        stats['pending'] = cursor.fetchone()['c']
        
        cursor.execute("SELECT i.name, COUNT(e.id) as c FROM institutes i LEFT JOIN exams e ON e.institute_id = i.id GROUP BY i.id")
        stats['by_institute'] = cursor.fetchall()
    finally:
        db.close()
    return stats

def get_upcoming_exams():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, i.name AS instructor_full_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            WHERE e.status = 'Scheduled'
              AND e.exam_date_time IS NOT NULL
              AND e.exam_date_time >= NOW()
            ORDER BY e.exam_date_time ASC, e.section ASC
        """)
        return cursor.fetchall()
    finally:
        db.close()

def get_already_scheduled_slots():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.room_id, e.instructor_id, e.exam_date_time, e.duration_minutes,
                   e.section, e.subject_type, e.subject_name, e.subject_id,
                   s.content_group_id
            FROM exams e
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
        """)
        return cursor.fetchall()
    finally:
        db.close()

def apply_schedule_results(scheduled, failed_ids):
    db = open_db()
    if not db: return
    try:
        cursor  = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        for item in scheduled:
            cursor.execute("""
                UPDATE exams SET room_id=%s, instructor_id=%s, instructor_name=%s, exam_date_time=%s, status='Scheduled' WHERE id=%s
            """, (item['room_id'], item['instructor_id'], item['instructor_name'], item['exam_date_time'], item['exam_id']))

            # ── Fetch exam details for notification messages ──────────────
            cursor_r.execute(
                "SELECT subject_name, section FROM exams WHERE id=%s", (item['exam_id'],)
            )
            exam_row = cursor_r.fetchone() or {}
            subject  = exam_row.get('subject_name') or 'Exam'
            section  = exam_row.get('section') or ''
            dt_str   = item['exam_date_time'].strftime('%b %d, %Y %I:%M %p') \
                       if hasattr(item['exam_date_time'], 'strftime') else str(item['exam_date_time'])

            # ── Notify assigned proctor (in-app) ─────────────────────────
            cursor_r.execute(
                "SELECT id FROM users WHERE instructor_id = %s AND role='proctor' LIMIT 1",
                (item['instructor_id'],)
            )
            proctor_user = cursor_r.fetchone()
            if proctor_user:
                create_notification(
                    proctor_user['id'],
                    f"📋 Proctoring Assignment: {subject}",
                    f"You have been assigned to proctor '{subject}'"
                    + (f" — Section {section}" if section else "")
                    + f" on {dt_str}."
                )

            # ── Notify all students in the section (in-app) ───────────────
            if section:
                cursor_r.execute(
                    "SELECT id FROM users WHERE role='student' AND section=%s",
                    (section,)
                )
                for student in cursor_r.fetchall():
                    create_notification(
                        student['id'],
                        f"📅 Exam Scheduled: {subject}",
                        f"Your exam for '{subject}' (Section {section}) has been scheduled"
                        f" on {dt_str}. Please check the timetable for room details."
                    )

        for eid in failed_ids:
            cursor.execute("UPDATE exams SET status='Unscheduled' WHERE id=%s", (eid,))
        db.commit()
    finally:
        db.close()

def reset_schedule():
    db = open_db()
    if not db: return
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)

        # ── Notify proctors and students BEFORE clearing ──────────────────
        # Collect all scheduled exams with their proctor and section
        cursor_r.execute("""
            SELECT e.id, e.subject_name, e.section, e.exam_date_time, e.instructor_id
            FROM exams e
            WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
        """)
        scheduled = cursor_r.fetchall()

        notified_proctors  = set()
        notified_students  = set()

        for exam in scheduled:
            subject = exam.get('subject_name') or 'an exam'
            section = (exam.get('section') or '').strip()

            # Notify each proctor once (they may proctor multiple exams)
            inst_id = exam.get('instructor_id')
            if inst_id and inst_id not in notified_proctors:
                cursor_r.execute(
                    "SELECT id FROM users WHERE instructor_id=%s AND role='proctor' LIMIT 1",
                    (inst_id,)
                )
                proctor = cursor_r.fetchone()
                if proctor:
                    create_notification(
                        proctor['id'],
                        "🔄 Schedule Reset by Admin",
                        "The exam schedule has been reset by the administrator. "
                        "All your proctoring assignments have been cleared. "
                        "A new schedule will be generated shortly."
                    )
                    notified_proctors.add(inst_id)

            # Notify each student in the section once
            if section:
                cursor_r.execute(
                    "SELECT id FROM users WHERE role='student' AND section=%s",
                    (section,)
                )
                for student in cursor_r.fetchall():
                    if student['id'] not in notified_students:
                        create_notification(
                            student['id'],
                            "🔄 Exam Schedule Reset",
                            f"The exam schedule for Section {section} has been reset by the administrator. "
                            "Your exam timetable will be updated once a new schedule is generated."
                        )
                        notified_students.add(student['id'])

        # ── Clear the schedule ────────────────────────────────────────────
        cursor.execute(
            "UPDATE exams SET room_id=NULL, instructor_id=NULL, instructor_name=NULL, "
            "exam_date_time=NULL, status='Pending'"
        )
        db.commit()
    finally:
        db.close()

def unschedule_exams(exam_ids):
    if not exam_ids: return
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        format_strings = ','.join(['%s'] * len(exam_ids))
        cursor.execute(
            f"UPDATE exams SET room_id=NULL, instructor_id=NULL, instructor_name=NULL, "
            f"exam_date_time=NULL, status='Pending' WHERE id IN ({format_strings})",
            tuple(exam_ids)
        )
        db.commit()
    finally:
        db.close()

def get_schedule_results():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, r.capacity, i.name AS instructor_name, inst.name as institute_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            ORDER BY e.exam_date_time ASC, e.section ASC
        """)
        return cursor.fetchall()
    finally:
        db.close()

def check_edit_conflicts(exam_id, new_room_id, new_instructor_id, new_datetime_str, duration_minutes):
    from datetime import datetime as _dt, timedelta as _td
    db = open_db()
    if not db: return ['Database connection failed.']
    conflicts = []
    try:
        cursor = db.cursor(dictionary=True)
        try:
            new_start = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_start = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')
        new_end = new_start + _td(minutes=duration_minutes)

        # Room conflict
        cursor.execute("SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE room_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL", (new_room_id, exam_id))
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str): r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                conflicts.append(f"⚠️ Room conflict: room is already used by '{row['subject_name']}' at {r_start}")

        # Proctor/instructor conflict
        cursor.execute("SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE instructor_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL", (new_instructor_id, exam_id))
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str): r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                conflicts.append(f"⚠️ Instructor conflict: proctor is already assigned to '{row['subject_name']}' at {r_start}")

        # Section conflict: same section cannot have two exams at the same time
        # + per-section daily exam limits (max 2 major, max 3 minor, max 3 total)
        cursor.execute(
            "SELECT section, subject_type FROM exams WHERE id=%s", (exam_id,)
        )
        this_exam = cursor.fetchone()
        if this_exam and this_exam.get('section'):
            section     = this_exam['section'].strip()
            new_is_major = (this_exam.get('subject_type') or 'Major') == 'Major'
            new_day      = new_start.date()

            cursor.execute(
                "SELECT subject_name, subject_type, exam_date_time, duration_minutes "
                "FROM exams "
                "WHERE section=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL",
                (section, exam_id)
            )
            day_major = 0; day_minor = 0; day_total = 0
            for row in cursor.fetchall():
                r_start = row['exam_date_time']
                if isinstance(r_start, str):
                    r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
                r_end = r_start + _td(minutes=row['duration_minutes'] or 60)

                # Simultaneous exam conflict AND 1 hour break
                new_buf_start = new_start - _td(hours=1)
                new_buf_end = new_end + _td(hours=1)
                if new_buf_start < r_end and r_start < new_buf_end:
                    conflicts.append(
                        f"⚠️ Section conflict: section '{section}' already has "
                        f"'{row['subject_name']}' at {r_start} (Requires 1hr break)"
                    )

                # Daily count (same date)
                if r_start.date() == new_day:
                    if (row.get('subject_type') or 'Major') == 'Major':
                        day_major += 1
                    else:
                        day_minor += 1
                    day_total += 1

            # Check daily limits for the proposed date
            minor_limit = 4 - day_major
            if new_is_major and day_major >= 3:
                conflicts.append(
                    f"⚠️ Daily limit: section '{section}' already has {day_major} major "
                    f"exam(s) on {new_day} (max 3 major per day)."
                )
            if not new_is_major and day_minor >= minor_limit:
                conflicts.append(
                    f"⚠️ Daily limit: section '{section}' already has {day_minor} minor exam(s) "
                    f"on {new_day} (max {minor_limit} minor allowed — {day_major} major already scheduled)."
                )
            if day_total >= 3:
                conflicts.append(
                    f"⚠️ Daily limit: section '{section}' already has {day_total} exam(s) "
                    f"on {new_day} (max 3 total per day)."
                )
    finally:
        db.close()
    return conflicts

def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str):
    from datetime import datetime as _dt
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        try:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')

        # ── Capture BEFORE state (old proctor, section, subject) ──────────
        cursor_r.execute(
            "SELECT subject_name, section, instructor_id, room_id, exam_date_time FROM exams WHERE id=%s",
            (exam_id,)
        )
        old = cursor_r.fetchone() or {}
        old_instructor_id = old.get('instructor_id')
        section  = (old.get('section') or '').strip()
        subject  = old.get('subject_name') or 'Exam'
        dt_str   = new_dt.strftime('%b %d, %Y %I:%M %p')

        # ── Apply update ───────────────────────────────────────────────────
        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_dt, exam_id)
        )
        db.commit()

        # ── Notify OLD proctor if they were replaced ───────────────────────
        if old_instructor_id and old_instructor_id != new_instructor_id:
            cursor_r.execute(
                "SELECT id, full_name FROM users WHERE instructor_id=%s AND role='proctor' LIMIT 1",
                (old_instructor_id,)
            )
            old_proctor = cursor_r.fetchone()
            if old_proctor:
                create_notification(
                    old_proctor['id'],
                    f"🔄 Proctoring Reassigned: {subject}",
                    f"You have been removed from proctoring '{subject}'"
                    + (f" — Section {section}" if section else "")
                    + f". The exam has been reassigned to another proctor."
                )

        # ── Notify NEW / CURRENT proctor ──────────────────────────────────
        cursor_r.execute(
            "SELECT id, full_name FROM users WHERE instructor_id=%s AND role='proctor' LIMIT 1",
            (new_instructor_id,)
        )
        new_proctor = cursor_r.fetchone()
        if new_proctor:
            if old_instructor_id and old_instructor_id != new_instructor_id:
                # Newly assigned
                msg = (
                    f"You have been assigned to proctor '{subject}'"
                    + (f" — Section {section}" if section else "")
                    + f" on {dt_str}."
                )
                title = f"📋 Proctoring Assignment: {subject}"
            else:
                # Same proctor, details updated
                msg = (
                    f"Your proctoring schedule for '{subject}'"
                    + (f" — Section {section}" if section else "")
                    + f" has been updated to {dt_str}."
                )
                title = f"📅 Schedule Updated: {subject}"
            create_notification(new_proctor['id'], title, msg)

        # ── Notify all students in the section ────────────────────────────
        if section:
            cursor_r.execute(
                "SELECT id FROM users WHERE role='student' AND section=%s",
                (section,)
            )
            for student in cursor_r.fetchall():
                create_notification(
                    student['id'],
                    f"📅 Exam Rescheduled: {subject}",
                    f"Your exam for '{subject}' (Section {section}) has been updated."
                    f" New schedule: {dt_str}. Please check the timetable for the latest room details."
                )

        return True
    finally:
        db.close()

def get_public_timetable(section=None, institute_id=None):
    # A student must have a section assigned — if not, show nothing.
    if not section or not section.strip():
        return []
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT e.subject_name, e.section, e.subject_type, e.exam_date_time, e.duration_minutes,
                   r.room_name, r.building, r.floor,
                   i.name AS proctor_name,
                   inst.code AS institute_code,
                   s.code AS subject_code
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.status = 'Scheduled'
              AND e.section = %s
        """
        params = [section.strip()]
        if institute_id:
            query += " AND e.institute_id = %s"
            params.append(institute_id)
        query += " ORDER BY e.exam_date_time ASC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        db.close()

# ── EXAM PERIOD ─────────────────────────────────────────────────────────────

def save_exam_period(period_start, period_end):
    db = open_db()
    if not db:
        return
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO exam_settings (id, period_start, period_end)
            VALUES (1, %s, %s)
            ON DUPLICATE KEY UPDATE period_start = VALUES(period_start),
                                    period_end   = VALUES(period_end)
        """, (period_start, period_end))
        db.commit()
    finally:
        db.close()


def get_exam_period():
    from datetime import date as _date
    db = open_db()
    if not db: return (None, None)
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT period_start, period_end FROM exam_settings WHERE id=1")
        row = cursor.fetchone()
        if row and row['period_start'] and row['period_end']:
            ps = row['period_start']
            pe = row['period_end']
            if not isinstance(ps, _date): ps = _date.fromisoformat(str(ps))
            if not isinstance(pe, _date): pe = _date.fromisoformat(str(pe))
            return (ps, pe)
        return (None, None)
    finally:
        db.close()


def save_exam_term(exam_term, exam_semester):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE exam_settings SET exam_term = %s, exam_semester = %s WHERE id = 1", (exam_term, exam_semester))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO exam_settings (id, exam_term, exam_semester) VALUES (1, %s, %s)", (exam_term, exam_semester))
        db.commit()
    finally:
        db.close()

def get_exam_term():
    db = open_db()
    if not db: return ("Midterm", "1st Semester")
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT exam_term, exam_semester FROM exam_settings WHERE id = 1")
        row = cursor.fetchone()
        if row:
            term = row.get('exam_term')
            sem = row.get('exam_semester')
            return (term if term else "Midterm", sem if sem else "1st Semester")
        return ("Midterm", "1st Semester")
    finally:
        db.close()

# ── PROCTOR AVAILABILITY ─────────────────────────────────────────────────────────────

def save_proctor_availability(instructor_id, entries):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM proctor_availability WHERE instructor_id=%s", (instructor_id,))
        for entry in entries:
            if isinstance(entry, dict):
                cursor.execute("INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                               (instructor_id, entry['date'], entry.get('start_time', '07:00'), entry.get('end_time', '20:00')))
            else:
                cursor.execute("INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, '07:00', '20:00')",
                               (instructor_id, entry))
        db.commit()
    finally:
        db.close()

def get_proctor_availability():
    from datetime import date as _date, time as _time, timedelta as _td
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT instructor_id, available_date, start_time, end_time FROM proctor_availability")
        res = {}
        for row in cursor.fetchall():
            iid = row['instructor_id']
            if iid not in res: res[iid] = []
            d = row['available_date']
            if not isinstance(d, _date): d = _date.fromisoformat(str(d))
            st, et = row.get('start_time'), row.get('end_time')
            if isinstance(st, _td): st = (datetime.min + st).time()
            elif isinstance(st, str): st = _time(int(st.split(':')[0]), int(st.split(':')[1]))
            elif st is None: st = _time(7, 0)
            if isinstance(et, _td): et = (datetime.min + et).time()
            elif isinstance(et, str): et = _time(int(et.split(':')[0]), int(et.split(':')[1]))
            elif et is None: et = _time(20, 0)
            res[iid].append({'date': d, 'start_time': st, 'end_time': et})
        return res
    finally:
        db.close()

def get_proctor_availability_for(instructor_id):
    from datetime import timedelta as _td, time as _time
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT available_date, start_time, end_time FROM proctor_availability WHERE instructor_id=%s ORDER BY available_date", (instructor_id,))
        entries = []
        for r in cursor.fetchall():
            st, et = r.get('start_time'), r.get('end_time')
            if isinstance(st, _td): st = (datetime.min + st).time().strftime('%H:%M')
            elif isinstance(st, _time): st = st.strftime('%H:%M')
            else: st = str(st)[:5] if st else '07:00'
            if isinstance(et, _td): et = (datetime.min + et).time().strftime('%H:%M')
            elif isinstance(et, _time): et = et.strftime('%H:%M')
            else: et = str(et)[:5] if et else '20:00'
            entries.append({'date': str(r['available_date']), 'start_time': st, 'end_time': et})
        return entries
    finally:
        db.close()

# ── PROCTOR EXAMS ─────────────────────────────────────────────────────────────

def get_proctor_exams(instructor_id):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.id, e.subject_name, e.section, e.exam_date_time, e.duration_minutes, e.status, r.room_name, r.capacity
            FROM exams e LEFT JOIN rooms r ON e.room_id = r.id
            WHERE e.instructor_id = %s AND e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL ORDER BY e.exam_date_time ASC, e.section ASC
        """, (instructor_id,))
        return cursor.fetchall()
    finally:
        db.close()

# ── RELIEVERS ─────────────────────────────────────────────────────────────

def add_reliever(exam_id, instructor_id, reason):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO relievers (exam_id, instructor_id, reason) VALUES (%s, %s, %s)", (exam_id, instructor_id, reason))
        db.commit()
    finally:
        db.close()

def get_relievers_for_exam(exam_id):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT r.*, i.name as instructor_name FROM relievers r LEFT JOIN instructors i ON r.instructor_id = i.id WHERE r.exam_id=%s", (exam_id,))
        return cursor.fetchall()
    finally:
        db.close()

def get_all_relievers():
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, i.name as instructor_name, e.subject_name, e.section, e.exam_date_time
            FROM relievers r
            LEFT JOIN instructors i ON r.instructor_id = i.id
            LEFT JOIN exams e ON r.exam_id = e.id
        """)
        return cursor.fetchall()
    finally:
        db.close()

def remove_reliever(id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM relievers WHERE id=%s", (id,))
        db.commit()
    finally:
        db.close()

# ── EXAM COLLECTION ─────────────────────────────────────────────────────────────

def get_exam_collection_status(institute_id=None):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        if institute_id:
            cursor.execute("""
                SELECT e.id as exam_id, e.subject_name, e.section, e.exam_date_time,
                       e.institute_id,
                       c.collected_by_instructor_id, c.collected_at, c.returned_at, c.notes,
                       inst.name as institute_name
                FROM exams e
                LEFT JOIN exam_collection c ON e.id = c.exam_id
                LEFT JOIN institutes inst ON e.institute_id = inst.id
                WHERE e.status = 'Scheduled' AND e.institute_id = %s
                ORDER BY e.exam_date_time ASC
            """, (institute_id,))
        else:
            cursor.execute("""
                SELECT e.id as exam_id, e.subject_name, e.section, e.exam_date_time,
                       e.institute_id,
                       c.collected_by_instructor_id, c.collected_at, c.returned_at, c.notes,
                       inst.name as institute_name
                FROM exams e
                LEFT JOIN exam_collection c ON e.id = c.exam_id
                LEFT JOIN institutes inst ON e.institute_id = inst.id
                WHERE e.status = 'Scheduled'
                ORDER BY e.exam_date_time ASC
            """)
        return cursor.fetchall()
    finally:
        db.close()

def mark_exam_collected(exam_id, collected_by_instructor_id, notes=''):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO exam_collection (exam_id, collected_by_instructor_id, collected_at, notes)
            VALUES (%s, %s, NOW(), %s)
            ON DUPLICATE KEY UPDATE collected_by_instructor_id=VALUES(collected_by_instructor_id), collected_at=NOW(), notes=VALUES(notes)
        """, (exam_id, collected_by_instructor_id, notes))
        db.commit()
    finally:
        db.close()

def mark_exam_returned(exam_id, notes=''):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE exam_collection SET returned_at=NOW(), notes=CONCAT(IFNULL(notes,''), '\n', %s) WHERE exam_id=%s", (notes, exam_id))
        db.commit()
    finally:
        db.close()

def get_collection_stats(institute_id=None):
    db = open_db()
    if not db: return {'total': 0, 'collected': 0, 'returned': 0, 'pending_collection': 0}
    try:
        cursor = db.cursor(dictionary=True)
        if institute_id:
            cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status='Scheduled' AND institute_id=%s", (institute_id,))
            total = cursor.fetchone()['c']
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.collected_at IS NOT NULL AND e.institute_id=%s
            """, (institute_id,))
            collected = cursor.fetchone()['c']
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.returned_at IS NOT NULL AND e.institute_id=%s
            """, (institute_id,))
            returned = cursor.fetchone()['c']
        else:
            cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status='Scheduled'")
            total = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM exam_collection WHERE collected_at IS NOT NULL")
            collected = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM exam_collection WHERE returned_at IS NOT NULL")
            returned = cursor.fetchone()['c']
        return {'total': total, 'collected': collected, 'returned': returned, 'pending_collection': total - collected}
    finally:
        db.close()

# ── PROCTOR ABSENCE ─────────────────────────────────────────────────────────────

def record_proctor_absence(instructor_id, exam_id, reason, reported_by):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO proctor_absence (instructor_id, exam_id, reason, reported_by, reported_at) VALUES (%s, %s, %s, %s, NOW())",
                       (instructor_id, exam_id, reason, reported_by))
        db.commit()
    finally:
        db.close()

def get_proctor_absence_report(date_from=None, date_to=None):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT p.*, i.name as instructor_name, e.subject_name, e.section, e.exam_date_time, u.full_name as reported_by
            FROM proctor_absence p
            LEFT JOIN instructors i ON p.instructor_id = i.id
            LEFT JOIN exams e ON p.exam_id = e.id
            LEFT JOIN users u ON p.reported_by = u.id
        """
        params = []
        if date_from and date_to:
            query += " WHERE p.reported_at >= %s AND p.reported_at <= %s"
            params.extend([date_from, date_to])
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        db.close()

def get_absence_stats():
    db = open_db()
    if not db: return {'total_absences': 0, 'instructors_with_absences': 0}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as c FROM proctor_absence")
        total = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(DISTINCT instructor_id) as c FROM proctor_absence")
        inst_count = cursor.fetchone()['c']
        return {'total_absences': total, 'instructors_with_absences': inst_count}
    finally:
        db.close()

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

def create_notification(user_id, title, message):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)", (user_id, title, message))
        db.commit()
    finally:
        db.close()

def get_notifications(user_id, unread_only=False):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM notifications WHERE user_id=%s"
        if unread_only: query += " AND is_read=0"
        query += " ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        db.close()

def get_unread_count(user_id):
    db = open_db()
    if not db: return 0
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as c FROM notifications WHERE user_id=%s AND is_read=0", (user_id,))
        return cursor.fetchone()['c']
    finally:
        db.close()

def mark_notification_read(notification_id, user_id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE notifications SET is_read=1 WHERE id=%s AND user_id=%s", (notification_id, user_id))
        db.commit()
    finally:
        db.close()

def mark_all_read(user_id):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (user_id,))
        db.commit()
    finally:
        db.close()

def create_notification_for_role(role, title, message):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE role=%s", (role,))
        users = cursor.fetchall()
        for u in users:
            cursor.execute("INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)", (u['id'], title, message))
        db.commit()
    finally:
        db.close()

# ── REPORTS ─────────────────────────────────────────────────────────────

def get_scheduling_report():
    stats = get_dashboard_stats()
    db = open_db()
    if not db: return stats
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT subject_type, COUNT(*) as c FROM exams GROUP BY subject_type")
        by_type = {r['subject_type']: r['c'] for r in cursor.fetchall()}
        stats['by_type'] = by_type
        return stats
    finally:
        db.close()

def get_assignment_report():
    return get_all_proctor_hours_summary()

def get_student_exam_load_report():
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT section, DATE(exam_date_time) as d, COUNT(*) as c FROM exams WHERE status='Scheduled' AND section IS NOT NULL GROUP BY section, DATE(exam_date_time)")
        res = {}
        for r in cursor.fetchall():
            sec = r['section']
            d = str(r['d'])
            if sec not in res: res[sec] = {}
            res[sec][d] = r['c']
        return {'by_section': res}
    finally:
        db.close()

# ── IMPORTERS ─────────────────────────────────────────────────────────────

def bulk_import_subjects(rows):
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                institute_id = None
                if 'institute_code' in row and row['institute_code']:
                    cursor.execute("SELECT id FROM institutes WHERE code=%s", (row['institute_code'],))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                cursor.execute("INSERT INTO subjects (name, code, institute_id, is_common, content_group_id) VALUES (%s, %s, %s, %s, %s)",
                               (row.get('name'), row.get('code'), institute_id, row.get('is_common', 0), row.get('content_group')))
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
        db.commit()
    finally:
        db.close()
    return (success_count, error_list)


def get_available_resources(exam_id, datetime_str, duration_minutes):
    from datetime import datetime as _dt, timedelta as _td
    db = open_db()
    if not db: return {'rooms': [], 'instructors': []}
    try:
        cursor = db.cursor(dictionary=True)
        try:
            new_start = _dt.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                new_start = _dt.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            except Exception:
                return {'rooms': [], 'instructors': []}
        new_end = new_start + _td(minutes=duration_minutes)

        cursor.execute("SELECT r.id, r.room_name as name, r.capacity FROM rooms r ORDER BY r.room_name")
        all_rooms = cursor.fetchall()

        cursor.execute("SELECT id, name FROM instructors WHERE status='Active' ORDER BY name")
        all_insts = cursor.fetchall()

        cursor.execute(
            "SELECT room_id, instructor_id, exam_date_time, duration_minutes FROM exams "
            "WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s",
            (exam_id,)
        )
        busy_rooms = set()
        busy_insts = set()
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str):
                r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                if row['room_id']: busy_rooms.add(row['room_id'])
                if row['instructor_id']: busy_insts.add(row['instructor_id'])

        # ── Check proctor_availability table ──
        proctor_avail = get_proctor_availability()
        exam_date = new_start.date()
        exam_start_time = new_start.time()
        exam_end_time = new_end.time()

        valid_insts = []
        for i in all_insts:
            iid = i['id']
            if iid in busy_insts:
                continue
            
            avail_entries = proctor_avail.get(iid)
            is_avail = True
            if avail_entries:
                has_entry_for_date = False
                time_match = False
                for entry in avail_entries:
                    if entry['date'] == exam_date:
                        has_entry_for_date = True
                        if exam_start_time >= entry['start_time'] and exam_end_time <= entry['end_time']:
                            time_match = True
                            break
                if has_entry_for_date and not time_match:
                    is_avail = False
            
            if is_avail:
                valid_insts.append({'id': i['id'], 'name': i['name']})

        return {
            'rooms': [{'id': r['id'], 'name': f"{r['name']} (Cap: {r['capacity']})"} for r in all_rooms if r['id'] not in busy_rooms],
            'instructors': valid_insts
        }
    finally:
        db.close()


def set_password_reset_token(email, token, expiry_dt):
    db = open_db()
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s", (token, expiry_dt, email))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()

def get_user_by_reset_token(token):
    db = open_db()
    if not db: return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE reset_token = %s", (token,))
        return cursor.fetchone()
    finally:
        db.close()

def clear_reset_token_and_update_password(token, new_hashed_password):
    db = open_db()
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET password = %s, reset_token = NULL, reset_token_expiry = NULL WHERE reset_token = %s", (new_hashed_password, token))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()


def get_user_by_email(email):
    db = open_db()
    if not db: return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        db.close()
