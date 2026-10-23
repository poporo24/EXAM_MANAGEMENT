import mysql.connector
from mysql.connector import pooling
from datetime import datetime, timedelta
import os, urllib.parse

_db_pool = None

def get_connection_pool():
    global _db_pool
    if _db_pool is None:
        db_url = os.environ.get('DATABASE_URL')
        pool_size = int(os.environ.get('DB_POOL_SIZE', 10))
        try:
            if db_url:
                url = urllib.parse.urlparse(db_url)
                _db_pool = pooling.MySQLConnectionPool(
                    pool_name="cca_exam_pool",
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=url.hostname,
                    user=url.username,
                    password=url.password,
                    database=url.path[1:],
                    port=url.port or 3306,
                    time_zone='+08:00'
                )
            else:
                _db_pool = pooling.MySQLConnectionPool(
                    pool_name="cca_exam_pool",
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=os.environ.get('DB_HOST', "127.0.0.1"),
                    user=os.environ.get('DB_USER', "root"),
                    password=os.environ.get('DB_PASSWORD', ""),
                    database=os.environ.get('DB_NAME', "cca_exam_management_db"),
                    port=int(os.environ.get('DB_PORT', 3306)),
                    time_zone='+08:00'
                )
        except Exception as pool_err:
            print(f"[DB Pool Init Notice] {pool_err}")
            _db_pool = None
    return _db_pool

def open_db():
    """
    Returns an active database connection from the connection pool with graceful fallback.
    Pooled connections automatically return to the pool when db.close() is called.
    """
    pool = get_connection_pool()
    if pool:
        try:
            return pool.get_connection()
        except Exception:
            pass  # Fallback to direct connection if pool is exhausted under extreme bursts

    db_url = os.environ.get('DATABASE_URL')
    try:
        if db_url:
            url = urllib.parse.urlparse(db_url)
            return mysql.connector.connect(
                host=url.hostname,
                user=url.username,
                password=url.password,
                database=url.path[1:],
                port=url.port or 3306,
                time_zone='+08:00'
            )
        else:
            return mysql.connector.connect(
                host=os.environ.get('DB_HOST', "127.0.0.1"),
                user=os.environ.get('DB_USER', "root"),
                password=os.environ.get('DB_PASSWORD', ""),
                database=os.environ.get('DB_NAME', "cca_exam_management_db"),
                port=int(os.environ.get('DB_PORT', 3306)),
                time_zone='+08:00'
            )
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

def ensure_database_schema():
    """
    Ensures required tables and schema columns exist in the database.
    Automatically runs on application startup to keep different environments
    (like local laptops or remote servers) in sync without manual migration.
    """
    db = open_db()
    if not db:
        return False, "Database connection failed"
    try:
        cursor = db.cursor()

        # 1. Create exam_archives table if missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_archives (
                id INT AUTO_INCREMENT PRIMARY KEY,
                academic_year VARCHAR(50) NOT NULL,
                exam_term VARCHAR(50) NOT NULL,
                exam_semester VARCHAR(50) NOT NULL,
                archive_title VARCHAR(150) NOT NULL,
                total_exams INT DEFAULT 0,
                total_proctors INT DEFAULT 0,
                total_sections INT DEFAULT 0,
                period_start DATE NULL,
                period_end DATE NULL,
                archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                archived_by INT NULL,
                archived_by_name VARCHAR(100) NULL,
                notes TEXT NULL,
                snapshot_data LONGTEXT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Check and add missing columns to system_settings
        cursor.execute("DESCRIBE system_settings")
        cols = {row[0].lower() for row in cursor.fetchall()}

        if 'max_daily_proctor_hrs' not in cols:
            cursor.execute("ALTER TABLE system_settings ADD COLUMN max_daily_proctor_hrs FLOAT NOT NULL DEFAULT 4.0")
        if 'schedule_published' not in cols:
            cursor.execute("ALTER TABLE system_settings ADD COLUMN schedule_published TINYINT(1) NOT NULL DEFAULT 0")
        if 'schedule_published_at' not in cols:
            cursor.execute("ALTER TABLE system_settings ADD COLUMN schedule_published_at DATETIME NULL")

        # 3. Create audit_logs table for security compliance and non-repudiation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INT NULL,
                user_name VARCHAR(150) NULL,
                user_role VARCHAR(50) NULL,
                ip_address VARCHAR(45) NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 4. Create schedule_reset_requests table for dual-authorization schedule reset workflow
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule_reset_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                requested_by_id INT NOT NULL,
                requested_by_name VARCHAR(150) NOT NULL,
                reason TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_by_id INT NULL,
                reviewed_by_name VARCHAR(150) NULL,
                reviewed_at DATETIME NULL,
                rejection_reason TEXT NULL,
                archive_id INT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        db.commit()
        return True, "Database schema is up to date."
    except Exception as e:
        print(f"ensure_database_schema notice: {e}")
        return False, str(e)
    finally:
        db.close()

def log_audit_event(action, details=None, user_id=None, user_name=None, user_role=None, ip_address=None, **kwargs):
    if not user_role and 'role' in kwargs:
        user_role = kwargs['role']
    """
    Logs security, administrative, and data modification events for compliance and non-repudiation.
    Aligned with ISO/IEC 27001 A.8.15 and NIST SP 800-53 AU-2.
    """
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, user_name, user_role, ip_address, action, details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, user_name, user_role, ip_address, action, details))
        db.commit()
    except Exception as e:
        print(f"[Audit Log Notice] {e}")
    finally:
        db.close()

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

def save_system_settings(day_start, day_end, slot_interval_min, max_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs=3.0, minor_duration_hrs=1.0, max_daily_proctor_hrs=4.0):
    db = open_db()
    if not db:
        return
    # Auto-normalize day_end if passed as 12-hour format (e.g., 08:00 -> 20:00 for 8:00 PM)
    if day_end:
        try:
            day_end_str = str(day_end).strip()
            parts = day_end_str.split(':')
            if len(parts) >= 2 and int(parts[0]) <= 11:
                day_end = f"{int(parts[0]) + 12:02d}:{parts[1]}"
        except Exception:
            pass
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO system_settings (id, day_start, day_end, slot_interval_min, max_consecutive_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs, minor_duration_hrs, max_daily_proctor_hrs)
            VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            day_start=VALUES(day_start), day_end=VALUES(day_end), slot_interval_min=VALUES(slot_interval_min), max_consecutive_proctor_hrs=VALUES(max_consecutive_proctor_hrs), travel_buffer_min=VALUES(travel_buffer_min), smtp_host=VALUES(smtp_host), smtp_port=VALUES(smtp_port), smtp_user=VALUES(smtp_user), smtp_password=VALUES(smtp_password), smtp_from=VALUES(smtp_from), smtp_use_tls=VALUES(smtp_use_tls), major_duration_hrs=VALUES(major_duration_hrs), minor_duration_hrs=VALUES(minor_duration_hrs), max_daily_proctor_hrs=VALUES(max_daily_proctor_hrs)
        """, (day_start, day_end, slot_interval_min, max_proctor_hrs, travel_buffer_min, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls, major_duration_hrs, minor_duration_hrs, max_daily_proctor_hrs))
        db.commit()
    finally:
        db.close()

def is_schedule_published():
    s = get_system_settings()
    return bool(s.get('schedule_published', 0))

def publish_schedule(user_id=None):
    """
    Publishes the current timetable, making it visible to students, proctors, and secretaries,
    and dispatches broadcast and finalized assignment notifications.
    """
    db = open_db()
    if not db: return False, "Database connection failed"
    try:
        cursor = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor.execute("UPDATE system_settings SET schedule_published = 1, schedule_published_at = NOW() WHERE id = 1")

        # Clear any old/stale draft schedule notifications before sending finalized ones
        cursor.execute("""
            DELETE FROM notifications
            WHERE title LIKE '%Proctoring Assignment:%'
               OR title LIKE '%Exam Scheduled:%'
               OR title = 'Exam Timetable Published'
        """)

        # 1. Broadcast official publication notice to all active students and proctors
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, created_at, is_read)
            SELECT u.id, 'Exam Timetable Published',
                   'The official exam timetable has been approved and published. Check your schedule now in your portal.',
                   NOW(), 0
            FROM users u
            WHERE u.role IN ('student', 'proctor') AND u.is_active = 1
        """)

        # 2. Send finalized proctoring assignment notifications for all scheduled exams
        cursor_r.execute("""
            SELECT e.subject_name, e.section, e.exam_date_time, u.id AS proctor_user_id
            FROM exams e
            JOIN users u ON u.instructor_id = e.instructor_id AND u.role = 'proctor'
            WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
            ORDER BY e.exam_date_time ASC
        """)
        notif_params = []
        for ex in cursor_r.fetchall():
            subj = ex.get('subject_name') or 'Exam'
            sec = ex.get('section') or ''
            dt_val = ex.get('exam_date_time')
            dt_str = dt_val.strftime('%b %d, %Y %I:%M %p') if hasattr(dt_val, 'strftime') else str(dt_val)
            notif_params.append((
                ex['proctor_user_id'],
                f"📋 Proctoring Assignment: {subj}",
                f"You have been assigned to proctor '{subj}'"
                + (f" — Section {sec}" if sec else "")
                + f" on {dt_str}."
            ))
        if notif_params:
            cursor.executemany(
                "INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)",
                notif_params
            )

        db.commit()
        return True, "Timetable has been officially published and distributed."
    except Exception as e:
        return False, str(e)
    finally:
        db.close()

def unpublish_schedule(user_id=None):
    """
    Reverts the timetable back to Draft mode, hiding it from non-admin portals
    and removing draft/published assignment notifications from proctors and students.
    """
    db = open_db()
    if not db: return False, "Database connection failed"
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE system_settings SET schedule_published = 0 WHERE id = 1")
        cursor.execute("""
            DELETE FROM notifications
            WHERE title LIKE '%Proctoring Assignment:%'
               OR title LIKE '%Exam Scheduled:%'
               OR title = 'Exam Timetable Published'
        """)
        db.commit()
        return True, "Timetable has been reverted to Draft mode."
    except Exception as e:
        return False, str(e)
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

def check_subjects_section_overlap(subject_ids):
    """Returns the name of a section if multiple subjects in subject_ids share that section."""
    if not subject_ids or len(subject_ids) < 2:
        return None
    db = open_db()
    if not db: return None
    try:
        cursor = db.cursor(dictionary=True)
        placeholders = ','.join(['%s'] * len(subject_ids))
        cursor.execute(f'''
            SELECT section, COUNT(DISTINCT subject_id) as sub_cnt
            FROM exams
            WHERE subject_id IN ({placeholders}) AND section IS NOT NULL AND TRIM(section) != ''
            GROUP BY section
            HAVING sub_cnt > 1
            LIMIT 1
        ''', tuple(subject_ids))
        row = cursor.fetchone()
        return row['section'] if row else None
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
            cursor.execute("INSERT INTO instructors (name, status, institute_id, is_pwd, subjects_taught) VALUES (%s, 'Inactive', %s, 0, '')", (full_name, institute_id))
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
        # Keep users.institute_id synced with linked instructors.institute_id for proctors
        try:
            cursor.execute("""
                UPDATE users u
                JOIN instructors i ON u.instructor_id = i.id
                SET u.institute_id = i.institute_id
                WHERE u.role = 'proctor' AND u.institute_id IS NULL AND i.institute_id IS NOT NULL
            """)
            db.commit()
        except Exception:
            pass
        cursor.execute("""
            SELECT u.id, u.full_name, u.full_name as name, u.email, u.role, u.section,
                   COALESCE(u.institute_id, i.institute_id) as institute_id,
                   u.is_super_admin,
                   inst.name as institute_name
            FROM users u
            LEFT JOIN instructors i ON u.instructor_id = i.id
            LEFT JOIN institutes inst ON COALESCE(u.institute_id, i.institute_id) = inst.id
            ORDER BY u.full_name
        """)
        return cursor.fetchall()
    finally:
        db.close()

def get_user_by_id(id):
    db = open_db()
    if not db: return {}
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.full_name, u.full_name as name, u.email, u.role, u.section,
                   COALESCE(u.institute_id, i.institute_id) as institute_id,
                   u.is_super_admin, u.instructor_id,
                   inst.name as institute_name
            FROM users u
            LEFT JOIN instructors i ON u.instructor_id = i.id
            LEFT JOIN institutes inst ON COALESCE(u.institute_id, i.institute_id) = inst.id
            WHERE u.id = %s
        """, (id,))
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
        old_role = user.get('role') if user else None

        # Security safeguard: Student accounts cannot be promoted to Admin or Super Admin
        if old_role == 'student':
            if role == 'admin':
                role = 'student'
            is_super_admin = 0
        if role == 'student':
            is_super_admin = 0
        
        # If changing to proctor and doesn't have instructor_id, create one
        if role == 'proctor' and not instructor_id:
            cursor.execute("INSERT INTO instructors (name, status, institute_id, is_pwd, subjects_taught) VALUES (%s, 'Active', %s, 0, '')", (full_name, institute_id))
            instructor_id = cursor.lastrowid
        elif role == 'proctor' and instructor_id:
            cursor.execute("UPDATE instructors SET name=%s, institute_id=%s WHERE id=%s", (full_name, institute_id, instructor_id))
            
        cursor.execute("UPDATE users SET full_name=%s, email=%s, role=%s, section=%s, institute_id=%s, is_super_admin=%s, instructor_id=%s WHERE id=%s",
                       (full_name, email, role, section, institute_id, is_super_admin, instructor_id, id))
        db.commit()
    finally:
        db.close()

def _cleanup_instructor_dependencies(cursor_w, inst_id):
    """Safely remove or unlink all references to an instructor_id before deleting the instructor record."""
    if not inst_id:
        return
    cursor_w.execute("UPDATE exams SET instructor_id = NULL WHERE instructor_id = %s", (inst_id,))
    cursor_w.execute("UPDATE exam_collection SET collected_by_instructor_id = NULL WHERE collected_by_instructor_id = %s", (inst_id,))
    cursor_w.execute("DELETE FROM proctor_availability WHERE instructor_id = %s", (inst_id,))
    cursor_w.execute("DELETE FROM proctor_absence WHERE instructor_id = %s", (inst_id,))
    cursor_w.execute("DELETE FROM relievers WHERE instructor_id = %s", (inst_id,))
    cursor_w.execute("UPDATE users SET instructor_id = NULL WHERE instructor_id = %s", (inst_id,))

def delete_user(id):
    db = open_db()
    if not db: return "DB connection error"
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, instructor_id, role FROM users WHERE id=%s", (id,))
        user = cursor.fetchone()
        if not user:
            return "User not found"
        
        cursor_w = db.cursor()
        cursor_w.execute("DELETE FROM notifications WHERE user_id=%s", (id,))
        if user.get('role') == 'proctor':
            inst_id = user.get('instructor_id')
            if not inst_id and user.get('full_name'):
                cursor.execute("SELECT id FROM instructors WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s)) LIMIT 1", (user['full_name'],))
                m = cursor.fetchone()
                if m:
                    inst_id = m['id']
            if inst_id:
                _cleanup_instructor_dependencies(cursor_w, inst_id)
                cursor_w.execute("DELETE FROM instructors WHERE id=%s", (inst_id,))
        cursor_w.execute("DELETE FROM users WHERE id=%s", (id,))
        db.commit()
        return None
    except Exception as e:
        return str(e)
    finally:
        db.close()

def bulk_delete_users_and_proctors(user_ids=None, delete_all_role=None, exclude_user_id=None):
    """
    Bulk delete selected user IDs or all users of a specific role (e.g. 'proctor').
    Never deletes Super Admin accounts or exclude_user_id.
    When deleting all proctors (or when no proctor users remain), also purges any orphaned rows in `instructors`.
    Returns (deleted_count, error_list).
    """
    db = open_db()
    if not db:
        return (0, ["Database connection failed"])
    deleted_count = 0
    errors = []
    try:
        cursor = db.cursor(dictionary=True)
        cursor_w = db.cursor()

        if delete_all_role == 'proctor':
            cursor.execute("SELECT id, instructor_id, full_name FROM users WHERE role = 'proctor' AND COALESCE(is_super_admin, 0) = 0")
            proctor_users = [u for u in cursor.fetchall() if u['id'] != exclude_user_id]
            for u in proctor_users:
                cursor_w.execute("DELETE FROM notifications WHERE user_id = %s", (u['id'],))
                cursor_w.execute("DELETE FROM users WHERE id = %s", (u['id'],))
                deleted_count += 1

            # Also clean up all instructor records so Faculty Management and User Management are both 100% clean
            cursor.execute("SELECT id FROM instructors")
            all_insts = cursor.fetchall()
            for inst in all_insts:
                iid = inst['id']
                _cleanup_instructor_dependencies(cursor_w, iid)
                cursor_w.execute("DELETE FROM instructors WHERE id = %s", (iid,))
            db.commit()
            return (deleted_count or len(all_insts), errors)

        target_ids = []
        if delete_all_role:
            cursor.execute("SELECT id FROM users WHERE role = %s AND COALESCE(is_super_admin, 0) = 0", (delete_all_role,))
            target_ids = [r['id'] for r in cursor.fetchall() if r['id'] != exclude_user_id]
        elif user_ids:
            for raw_id in user_ids:
                try:
                    uid = int(raw_id)
                    if uid != exclude_user_id:
                        target_ids.append(uid)
                except ValueError:
                    continue

        for uid in target_ids:
            cursor.execute("SELECT id, full_name, email, instructor_id, role, is_super_admin FROM users WHERE id = %s", (uid,))
            user = cursor.fetchone()
            if not user:
                continue
            if user.get('is_super_admin'):
                errors.append(f"Skipped Super Admin '{user.get('full_name')}'")
                continue
            try:
                cursor_w.execute("DELETE FROM notifications WHERE user_id = %s", (uid,))
                if user.get('role') == 'proctor':
                    inst_id = user.get('instructor_id')
                    if not inst_id and user.get('full_name'):
                        cursor.execute("SELECT id FROM instructors WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s)) LIMIT 1", (user['full_name'],))
                        m = cursor.fetchone()
                        if m:
                            inst_id = m['id']
                    if inst_id:
                        _cleanup_instructor_dependencies(cursor_w, inst_id)
                        cursor_w.execute("DELETE FROM instructors WHERE id = %s", (inst_id,))
                cursor_w.execute("DELETE FROM users WHERE id = %s", (uid,))
                deleted_count += 1
            except Exception as row_err:
                errors.append(f"{user.get('full_name')}: {row_err}")

        # If all proctor user accounts have now been deleted, also clean up any orphaned instructor records
        cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'proctor'")
        rem = cursor.fetchone()
        if rem and rem['cnt'] == 0:
            cursor.execute("SELECT id FROM instructors")
            for inst in cursor.fetchall():
                _cleanup_instructor_dependencies(cursor_w, inst['id'])
                cursor_w.execute("DELETE FROM instructors WHERE id = %s", (inst['id'],))

        db.commit()
        return (deleted_count, errors)
    except Exception as e:
        return (deleted_count, [str(e)])
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
        cursor.execute("""
            SELECT u.id, u.full_name, u.full_name as name, u.email, u.section, u.institute_id, u.created_at,
                   inst.name as institute_name
            FROM users u
            LEFT JOIN institutes inst ON u.institute_id = inst.id
            WHERE u.role IN ('student', 'proctor') AND u.is_active=0
            ORDER BY u.created_at DESC
        """)
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
        # Also activate instructor record if this user is a proctor
        cursor.execute("""
            UPDATE instructors i
            JOIN users u ON u.instructor_id = i.id
            SET i.status = 'Active'
            WHERE u.id = %s AND u.role = 'proctor'
        """, (user_id,))
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
    """Deactivate a student or proctor account (is_active=0) and notify them."""
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor.execute("UPDATE users SET is_active=0 WHERE id=%s AND role IN ('student', 'proctor')", (user_id,))
        cursor.execute("""
            UPDATE instructors i
            JOIN users u ON u.instructor_id = i.id
            SET i.status = 'Inactive'
            WHERE u.id = %s AND u.role = 'proctor'
        """, (user_id,))
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
        cursor_r = db.cursor(dictionary=True)
        cursor_r.execute("SELECT id, LOWER(TRIM(room_name)) as rname FROM rooms")
        existing_rooms = {r['rname']: r['id'] for r in cursor_r.fetchall()}
        
        # Pre-cache institute codes to avoid repeated queries
        cursor_r.execute("SELECT id, UPPER(code) as code FROM institutes WHERE code IS NOT NULL")
        inst_cache = {i['code']: i['id'] for i in cursor_r.fetchall()}
        
        for i, row in enumerate(rows):
            try:
                r_name = (row.get('room_name') or '').strip()
                if not r_name:
                    continue
                institute_id = row.get('institute_id')
                if not institute_id and row.get('institute_code'):
                    institute_id = inst_cache.get(row['institute_code'].strip().upper())
                
                k = r_name.lower()
                cap = int(row.get('capacity', 30) or 30)
                bld = row.get('building', '')
                flr = int(row.get('floor', 1) or 1)
                pwd = int(row.get('pwd_accessible', 0) or 0)
                
                if k in existing_rooms:
                    cursor.execute("""
                        UPDATE rooms
                        SET capacity=%s, building=%s, floor=%s, institute_id=%s, is_pwd_accessible=%s
                        WHERE id=%s
                    """, (cap, bld, flr, institute_id, pwd, existing_rooms[k]))
                else:
                    cursor.execute("""
                        INSERT INTO rooms (room_name, capacity, building, floor, institute_id, is_pwd_accessible)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (r_name, cap, bld, flr, institute_id, pwd))
                    existing_rooms[k] = cursor.lastrowid
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
        rows = cursor.fetchall()
        for r in rows:
            if 'total_hours' in r and r['total_hours'] is not None:
                tot = float(r['total_hours'])
                r['total_hours'] = int(tot) if tot.is_integer() else round(tot, 1)
        return rows
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

        global _cached_proctor_pw_hash
        if '_cached_proctor_pw_hash' not in globals() or not _cached_proctor_pw_hash:
            _cached_proctor_pw_hash = hash_password(proctor_password)
        hashed = _cached_proctor_pw_hash
        cursor.execute("INSERT INTO users (full_name, email, password, role, instructor_id, institute_id) VALUES (%s, %s, %s, 'proctor', %s, %s)",
                       (name, proctor_email, hashed, instructor_id, institute_id))
        db.commit()
        return instructor_id
    finally:
        db.close()

def edit_instructor(id, name, institute_id, building, is_pwd, subjects_taught):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE instructors SET name=%s, institute_id=%s, building=%s, is_pwd=%s, subjects_taught=%s WHERE id=%s",
                       (name, institute_id, building, is_pwd, subjects_taught, id))
        cursor.execute("UPDATE users SET full_name=%s, institute_id=%s WHERE instructor_id=%s AND role='proctor'",
                       (name, institute_id, id))
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
        cursor_w = db.cursor()
        # Find any linked proctor user accounts so they are also removed from User Management
        cursor.execute("SELECT id FROM users WHERE instructor_id = %s AND role = 'proctor' AND COALESCE(is_super_admin, 0) = 0", (instructor_id,))
        linked_users = cursor.fetchall()
        for u in linked_users:
            cursor_w.execute("DELETE FROM notifications WHERE user_id = %s", (u['id'],))
            cursor_w.execute("DELETE FROM users WHERE id = %s", (u['id'],))

        _cleanup_instructor_dependencies(cursor_w, instructor_id)
        cursor_w.execute("DELETE FROM instructors WHERE id = %s", (instructor_id,))
        db.commit()
        return None
    except Exception as e:
        return f'Delete failed: {e}'
    finally:
        db.close()

def bulk_import_instructors(rows):
    from datetime import timedelta as _td, date as _date
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    
    # Get exam period for date mapping
    period_start, period_end = get_exam_period()
    if not period_start or not period_end:
        period_start = _date(2026, 11, 2)
        period_end   = _date(2026, 11, 7)
    day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                institute_id = row.get('institute_id')
                if not institute_id and row.get('institute_code'):
                    cursor.execute("SELECT id FROM institutes WHERE UPPER(code)=UPPER(%s)", (row['institute_code'].strip(),))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                
                name_val = (row.get('name') or '').strip()
                if not name_val:
                    continue

                # Smart upsert: if instructor with this name already exists, update their institute, building, subjects, and status
                cursor.execute("SELECT id FROM instructors WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s)) LIMIT 1", (name_val,))
                existing = cursor.fetchone()
                if existing:
                    inst_id = existing[0]
                    cursor.execute("""
                        UPDATE instructors
                        SET institute_id = COALESCE(%s, institute_id),
                            building = CASE WHEN %s IS NOT NULL AND %s != '' THEN %s ELSE building END,
                            is_pwd = %s,
                            subjects_taught = CASE WHEN %s IS NOT NULL AND %s != '' THEN %s ELSE subjects_taught END,
                            status = 'Active'
                        WHERE id = %s
                    """, (
                        institute_id,
                        row.get('building'), row.get('building'), row.get('building'),
                        int(row.get('is_pwd', 0) or 0),
                        row.get('subjects_taught'), row.get('subjects_taught'), row.get('subjects_taught'),
                        inst_id
                    ))
                    if institute_id:
                        cursor.execute("UPDATE users SET institute_id = %s WHERE instructor_id = %s", (institute_id, inst_id))
                    db.commit()
                else:
                    db.commit()
                    inst_id = add_instructor(
                        name_val,
                        institute_id,
                        row.get('building'),
                        row.get('is_pwd', 0),
                        row.get('subjects_taught', ''),
                        provided_email=row.get('email', '')
                    )
                
                # Save availability if present
                if inst_id and 'availability' in row and row['availability'] and period_start and period_end:
                    avail_entries = []
                    for avail in row['availability']:
                        target_wd = day_map.get(avail['day'])
                        if target_wd is not None:
                            curr = period_start
                            while curr <= period_end:
                                if curr.weekday() == target_wd:
                                    avail_entries.append({
                                        'date': curr.isoformat(),
                                        'start_time': avail['start'],
                                        'end_time': avail['end']
                                    })
                                curr += _td(days=1)
                    if avail_entries:
                        save_proctor_availability(inst_id, avail_entries)
                
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
    finally:
        db.close()
    return (success_count, error_list)

def get_proctor_total_hours(instructor_id, date_from=None, date_to=None):
    db = open_db()
    if not db: return 0
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT SUM(duration_minutes) as tot FROM exams WHERE instructor_id=%s AND status='Scheduled'"
        params = [instructor_id]
        if date_from and date_to:
            query += " AND exam_date_time >= %s AND exam_date_time <= %s"
            params.extend([date_from, date_to])
        cursor.execute(query, tuple(params))
        res = cursor.fetchone()
        tot = float(res['tot'] or 0) / 60.0
        return int(tot) if tot.is_integer() else round(tot, 1)
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
        rows = cursor.fetchall()
        for r in rows:
            tot = float(r.get('total_hours') or 0.0)
            r['total_hours'] = int(tot) if tot.is_integer() else round(tot, 1)
        return rows
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
        st_norm = str(subject_type or '').strip().lower()
        subject_type = 'Minor' if st_norm in ('minor', 'laboratory', 'lab') else 'Major'
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
    """Insert or update multiple exams from parsed CSV rows.
    Each row dict: subject_name, section, subject_type, institute_id (resolved).
    Duration is auto-set from system settings based on subject_type.
    Prevents duplicate (subject_name, section) entries on re-import.
    Returns (success_count, error_list)."""
    db = open_db()
    if not db: return (0, ["DB Error"])
    settings = get_system_settings()
    major_min = int(float(settings.get('major_duration_hrs', 3.0) or 3.0) * 60)
    minor_min = int(float(settings.get('minor_duration_hrs', 1)) * 60)
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor_r.execute("SELECT id, subject_name, section FROM exams")
        existing_map = {}
        for ex in cursor_r.fetchall():
            k = ((ex.get('subject_name') or '').strip().lower(), (ex.get('section') or '').strip().upper())
            existing_map[k] = ex['id']

        insert_batch = []
        for i, row in enumerate(rows):
            try:
                subject_type = row.get('subject_type', 'Major')
                dur_min = minor_min if subject_type in ('Minor', 'Laboratory') else major_min
                s_name = (row.get('subject_name') or '').strip()
                sec = (row.get('section') or '').strip() or None
                key = (s_name.lower(), (sec or '').upper())
                if key in existing_map:
                    cursor.execute(
                        """UPDATE exams
                           SET subject_type=%s, duration_minutes=%s, institute_id=%s, subject_id=%s,
                               status='Pending', exam_date_time=NULL, room_id=NULL, instructor_id=NULL, instructor_name=NULL
                           WHERE id=%s""",
                        (subject_type, dur_min, row.get('institute_id'), row.get('subject_id'), existing_map[key])
                    )
                else:
                    insert_batch.append((
                        s_name, sec, subject_type, dur_min,
                        row.get('institute_id'), row.get('subject_id')
                    ))
                    existing_map[key] = -1
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")

        if insert_batch:
            cursor.executemany(
                """INSERT INTO exams (subject_name, section, subject_type, duration_minutes, status, institute_id, subject_id)
                   VALUES (%s, %s, %s, %s, 'Pending', %s, %s)""",
                insert_batch
            )
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
            SELECT e.*, s.content_group_id, s.code AS subject_code, s.name AS subject_catalog_name,
                   COALESCE(inst.capacity_default, 40) AS institute_capacity_default,
                   COALESCE(u_cnt.stu_cnt, 0) AS section_student_count
            FROM exams e
            LEFT JOIN subjects s ON e.subject_id = s.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            LEFT JOIN (
                SELECT section, COUNT(*) AS stu_cnt
                FROM users
                WHERE role = 'student' AND section IS NOT NULL
                GROUP BY section
            ) u_cnt ON u_cnt.section = e.section
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

def sync_exam_and_subject_institutes():
    """
    1. Automatically removes duplicate (subject_name, section) rows in exams (caused by importing CSV multiple times).
    2. Ensures all exams and subjects have consistent CCA institute assignments in bulk (fewest SQL queries).
    """
    import re as _re
    from collections import defaultdict as _dd
    db = open_db()
    if not db:
        return
    try:
        cursor = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        cursor_r.execute("SELECT id, UPPER(TRIM(code)) AS code FROM institutes WHERE code IS NOT NULL")
        inst_by_code = {r['code']: r['id'] for r in cursor_r.fetchall() if r.get('code')}
        if not inst_by_code:
            return

        prefix_to_code = {
            'C': 'ICSLIS', 'CS': 'ICSLIS', 'I': 'ICSLIS', 'IS': 'ICSLIS', 'ACT': 'ICSLIS', 'L': 'ICSLIS', 'LIS': 'ICSLIS',
            'A': 'IBM', 'BSA': 'IBM', 'AI': 'IBM', 'AIS': 'IBM', 'BSAIS': 'IBM', 'E': 'IBM', 'BSE': 'IBM', 'T': 'IBM', 'BSTM': 'IBM',
            'BPE': 'IEAS', 'TE': 'IEAS', 'BTLE': 'IEAS', 'BSNE': 'IEAS', 'PSYCH': 'IEAS', 'BAELS': 'IEAS', 'M': 'IEAS', 'COMM': 'IEAS'
        }

        cursor_r.execute("SELECT id, section, institute_id, subject_id, subject_name, status FROM exams ORDER BY (status = 'Scheduled') DESC, id ASC")
        exam_rows = cursor_r.fetchall()

        seen_keys = set()
        dup_exam_ids = []
        ids_by_target_inst = _dd(list)
        subj_inst_sets = _dd(set)

        for ex in exam_rows:
            s_name = (ex.get('subject_name') or '').strip().lower()
            sec = (ex.get('section') or '').strip()
            dedup_key = (s_name, sec.upper())
            if dedup_key in seen_keys:
                dup_exam_ids.append(ex['id'])
                continue
            seen_keys.add(dedup_key)

            m = _re.match(r'^[A-Za-z]+', sec)
            pref = m.group(0).upper() if m else ''
            target_code = prefix_to_code.get(pref)
            target_inst_id = inst_by_code.get(target_code) if target_code else ex.get('institute_id')
            if target_inst_id and target_inst_id != ex.get('institute_id'):
                ids_by_target_inst[target_inst_id].append(ex['id'])
            eff_inst_id = target_inst_id or ex.get('institute_id')
            sid = ex.get('subject_id')
            if sid and eff_inst_id:
                subj_inst_sets[sid].add(eff_inst_id)

        if dup_exam_ids:
            placeholders = ",".join(["%s"] * len(dup_exam_ids))
            dup_tuple = tuple(dup_exam_ids)
            cursor.execute(f"DELETE FROM exam_collection WHERE exam_id IN ({placeholders})", dup_tuple)
            cursor.execute(f"DELETE FROM relievers WHERE exam_id IN ({placeholders})", dup_tuple)
            cursor.execute(f"DELETE FROM proctor_absence WHERE exam_id IN ({placeholders})", dup_tuple)
            cursor.execute(f"DELETE FROM exams WHERE id IN ({placeholders})", dup_tuple)

        # Bulk update exams by target institute (at most 3 UPDATE queries instead of 1000+)
        for target_inst_id, eid_list in ids_by_target_inst.items():
            placeholders = ",".join(["%s"] * len(eid_list))
            cursor.execute(
                f"UPDATE exams SET institute_id = %s WHERE id IN ({placeholders})",
                tuple([target_inst_id] + eid_list)
            )

        # Bulk update subjects by (institute_id, is_common)
        sids_by_inst_common = _dd(list)
        for sid, inst_ids in subj_inst_sets.items():
            if len(inst_ids) == 1:
                only_inst = next(iter(inst_ids))
                sids_by_inst_common[(only_inst, 0)].append(sid)
            elif len(inst_ids) > 1:
                ieas_id = inst_by_code.get('IEAS') or next(iter(inst_ids))
                sids_by_inst_common[(ieas_id, 1)].append(sid)

        for (target_inst_id, is_common_flag), sid_list in sids_by_inst_common.items():
            placeholders = ",".join(["%s"] * len(sid_list))
            cursor.execute(
                f"UPDATE subjects SET institute_id = %s, is_common = %s WHERE id IN ({placeholders})",
                tuple([target_inst_id, is_common_flag] + sid_list)
            )

        db.commit()
    except Exception as e:
        print("[sync_exam_and_subject_institutes error]", e)
    finally:
        db.close()

def apply_schedule_results(scheduled, failed_ids):
    is_pub = is_schedule_published()
    db = open_db()
    if not db: return
    try:
        cursor  = db.cursor()
        cursor_r = db.cursor(dictionary=True)

        if scheduled:
            # Batch UPDATE in chunks of 200 rows using CASE WHEN so 1,000+ exams update in 5 fast queries
            chunk_size = 200
            for start_idx in range(0, len(scheduled), chunk_size):
                chunk = scheduled[start_idx:start_idx + chunk_size]
                room_cases, inst_cases, name_cases, dt_cases, ids = [], [], [], [], []
                params_room, params_inst, params_name, params_dt = [], [], [], []
                for item in chunk:
                    eid = int(item['exam_id'])
                    ids.append(eid)
                    room_cases.append("WHEN %s THEN %s")
                    params_room.extend([eid, item['room_id']])
                    inst_cases.append("WHEN %s THEN %s")
                    params_inst.extend([eid, item['instructor_id']])
                    name_cases.append("WHEN %s THEN %s")
                    params_name.extend([eid, item['instructor_name']])
                    dt_cases.append("WHEN %s THEN %s")
                    params_dt.extend([eid, item['exam_date_time']])
                id_placeholders = ",".join(["%s"] * len(ids))
                sql = f"""
                    UPDATE exams
                    SET room_id = CASE id {' '.join(room_cases)} END,
                        instructor_id = CASE id {' '.join(inst_cases)} END,
                        instructor_name = CASE id {' '.join(name_cases)} END,
                        exam_date_time = CASE id {' '.join(dt_cases)} END,
                        status = 'Scheduled'
                    WHERE id IN ({id_placeholders})
                """
                all_params = tuple(params_room + params_inst + params_name + params_dt + ids)
                cursor.execute(sql, all_params)

            if is_pub:
                cursor_r.execute("SELECT instructor_id, id FROM users WHERE role='proctor' AND instructor_id IS NOT NULL")
                proctor_user_map = {r['instructor_id']: r['id'] for r in cursor_r.fetchall()}
                notif_rows = []
                for item in scheduled:
                    p_uid = proctor_user_map.get(item.get('instructor_id'))
                    if p_uid:
                        subject = item.get('subject_name') or 'Exam'
                        section = item.get('section') or ''
                        dt_val = item.get('exam_date_time')
                        dt_str = dt_val.strftime('%b %d, %Y %I:%M %p') if hasattr(dt_val, 'strftime') else str(dt_val)
                        notif_rows.append((
                            p_uid,
                            f"📋 Proctoring Assignment: {subject}",
                            f"You have been assigned to proctor '{subject}'"
                            + (f" — Section {section}" if section else "")
                            + f" on {dt_str}."
                        ))
                if notif_rows:
                    cursor.executemany(
                        "INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)",
                        notif_rows
                    )

        if failed_ids:
            placeholders = ",".join(["%s"] * len(failed_ids))
            cursor.execute(
                f"UPDATE exams SET status='Unscheduled' WHERE id IN ({placeholders})",
                tuple(int(eid) for eid in failed_ids)
            )
        db.commit()
    finally:
        db.close()

def reset_schedule():
    was_published = is_schedule_published()
    db = open_db()
    if not db: return
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)

        # Clean up any draft/published assignment notifications
        cursor.execute("""
            DELETE FROM notifications
            WHERE title LIKE '%Proctoring Assignment:%'
               OR title LIKE '%Exam Scheduled:%'
               OR title = 'Exam Timetable Published'
        """)

        # ── Notify proctors and students BEFORE clearing (ONLY if schedule was live/published) ──
        if was_published:
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, created_at, is_read)
                SELECT DISTINCT u.id,
                       '🔄 Schedule Reset by Admin',
                       'The exam schedule has been reset by the administrator. All your proctoring assignments have been cleared. A new schedule will be generated shortly.',
                       NOW(), 0
                FROM exams e
                JOIN users u ON u.instructor_id = e.instructor_id AND u.role = 'proctor'
                WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
            """)
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, created_at, is_read)
                SELECT DISTINCT u.id,
                       '🔄 Exam Schedule Reset',
                       CONCAT('The exam schedule for Section ', u.section, ' has been reset by the administrator. Your exam timetable will be updated once a new schedule is generated.'),
                       NOW(), 0
                FROM exams e
                JOIN users u ON u.section = e.section AND u.role = 'student'
                WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL AND e.section IS NOT NULL AND e.section != ''
            """)

        # ── Clear the schedule & associated schedule records ──────────────
        cursor.execute("DELETE FROM exam_collection")
        cursor.execute("DELETE FROM relievers")
        cursor.execute("DELETE FROM proctor_absence")
        cursor.execute("UPDATE system_settings SET schedule_published = 0 WHERE id = 1")
        cursor.execute(
            "UPDATE exams SET room_id=NULL, instructor_id=NULL, instructor_name=NULL, "
            "exam_date_time=NULL, status='Pending'"
        )
        db.commit()
    finally:
        db.close()

def create_schedule_reset_request(user_id, user_name, reason):
    """
    Submits a schedule reset request from a System Admin for Super Admin approval.
    Enforces the 'Four-Eyes Principle' (Dual Authorization) to prevent accidental wipes.
    """
    if not reason or not reason.strip():
        return False, "A reason explaining why the schedule must be reset is required."
    
    db = open_db()
    if not db:
        return False, "Database connection failed."
    try:
        cursor = db.cursor(dictionary=True)
        # Check if there is already an active pending request
        cursor.execute("SELECT id, requested_by_name, requested_at FROM schedule_reset_requests WHERE status = 'pending'")
        existing = cursor.fetchone()
        if existing:
            return False, f"A schedule reset request is already pending Super Admin approval (submitted by {existing['requested_by_name']})."
        
        # Insert new request
        cursor.execute("""
            INSERT INTO schedule_reset_requests (requested_by_id, requested_by_name, reason, status, requested_at)
            VALUES (%s, %s, %s, 'pending', NOW())
        """, (user_id, user_name, reason.strip()))
        req_id = cursor.lastrowid

        # Notify all Super Admins
        cursor.execute("SELECT id FROM users WHERE is_super_admin = 1 AND is_active = 1")
        for sa in cursor.fetchall():
            create_notification(
                sa['id'],
                "⚠️ Schedule Reset Request Pending",
                f"Admin {user_name} has requested to reset the master timetable. Reason: \"{reason.strip()}\". Please review and approve/reject in the Super Admin panel."
            )
        
        db.commit()
        log_audit_event('SCHEDULE_RESET_REQUESTED', f"Admin {user_name} requested schedule reset. Reason: {reason.strip()}", user_id=user_id, user_name=user_name, user_role='admin')
        return True, "Schedule reset request submitted. A Super Administrator has been notified to review and authorize the action."
    except Exception as e:
        return False, f"Failed to submit reset request: {e}"
    finally:
        db.close()

def get_pending_schedule_reset_request():
    """Returns the current pending schedule reset request, if any."""
    db = open_db()
    if not db: return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, requested_by_id, requested_by_name, reason, status, requested_at
            FROM schedule_reset_requests
            WHERE status = 'pending'
            ORDER BY id DESC LIMIT 1
        """)
        return cursor.fetchone()
    finally:
        db.close()

def get_all_schedule_reset_requests(pending_only=False):
    """Returns schedule reset requests for review."""
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        if pending_only:
            cursor.execute("""
                SELECT id, requested_by_id, requested_by_name, reason, status, requested_at
                FROM schedule_reset_requests
                WHERE status = 'pending'
                ORDER BY id DESC
            """)
        else:
            cursor.execute("""
                SELECT id, requested_by_id, requested_by_name, reason, status, requested_at,
                       reviewed_by_id, reviewed_by_name, reviewed_at, rejection_reason, archive_id
                FROM schedule_reset_requests
                ORDER BY id DESC LIMIT 50
            """)
        return cursor.fetchall()
    finally:
        db.close()

def approve_schedule_reset_request(request_id, reviewer_id, reviewer_name):
    """
    Authorizes and executes a pending schedule reset request.
    Automatically captures a permanent archive snapshot before wiping.
    """
    db = open_db()
    if not db: return False, "Database connection failed."
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schedule_reset_requests WHERE id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, "Schedule reset request not found."
        if req['status'] != 'pending':
            return False, f"This request has already been {req['status']}."
        
        # 1. Capture snapshot before reset
        term_tuple = get_exam_term()
        exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
        exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
        ok_arch, res_arch = create_exam_archive(
            academic_year="2025-2026",
            exam_term=exam_term,
            exam_semester=exam_semester,
            archive_title=None,
            notes=f"Archived prior to approved reset. (Requested by: {req['requested_by_name']}, Approved by: {reviewer_name}). Reason: {req['reason']}",
            user_id=reviewer_id,
            user_name=reviewer_name
        )
        archive_id = res_arch if (ok_arch and isinstance(res_arch, int)) else None

        # 2. Execute master schedule reset
        reset_schedule()

        # 3. Update request record
        cursor.execute("""
            UPDATE schedule_reset_requests
            SET status = 'approved', reviewed_by_id = %s, reviewed_by_name = %s, reviewed_at = NOW(), archive_id = %s
            WHERE id = %s
        """, (reviewer_id, reviewer_name, archive_id, request_id))
        db.commit()

        # 4. Notify requester
        create_notification(
            req['requested_by_id'],
            "✅ Schedule Reset Approved",
            f"Your schedule reset request has been approved by Super Admin {reviewer_name}. The schedule has been safely archived and reset to pending."
        )

        log_audit_event('SCHEDULE_RESET_APPROVED', f"Super Admin {reviewer_name} approved reset request #{request_id} from {req['requested_by_name']}. Archive created.", user_id=reviewer_id, user_name=reviewer_name, user_role='super_admin')
        return True, "Schedule reset approved and executed. An archive snapshot has been saved."
    except Exception as e:
        return False, f"Error approving reset: {e}"
    finally:
        db.close()

def reject_schedule_reset_request(request_id, reviewer_id, reviewer_name, rejection_reason=""):
    """Rejects a pending schedule reset request."""
    db = open_db()
    if not db: return False, "Database connection failed."
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM schedule_reset_requests WHERE id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, "Schedule reset request not found."
        if req['status'] != 'pending':
            return False, f"This request has already been {req['status']}."
        
        cursor.execute("""
            UPDATE schedule_reset_requests
            SET status = 'rejected', reviewed_by_id = %s, reviewed_by_name = %s, reviewed_at = NOW(), rejection_reason = %s
            WHERE id = %s
        """, (reviewer_id, reviewer_name, rejection_reason.strip() if rejection_reason else None, request_id))
        db.commit()

        # Notify requester
        create_notification(
            req['requested_by_id'],
            "❌ Schedule Reset Request Declined",
            f"Your schedule reset request was declined by Super Admin {reviewer_name}." + (f" Reason: {rejection_reason.strip()}" if rejection_reason else "")
        )

        log_audit_event('SCHEDULE_RESET_REJECTED', f"Super Admin {reviewer_name} rejected reset request #{request_id} from {req['requested_by_name']}. Reason: {rejection_reason}", user_id=reviewer_id, user_name=reviewer_name, user_role='super_admin')
        return True, "Schedule reset request has been declined."
    except Exception as e:
        return False, f"Error rejecting request: {e}"
    finally:
        db.close()

def unschedule_exams(exam_ids):
    if not exam_ids: return
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        format_strings = ','.join(['%s'] * len(exam_ids))
        cursor.execute(f"DELETE FROM exam_collection WHERE exam_id IN ({format_strings})", tuple(exam_ids))
        cursor.execute(f"DELETE FROM relievers WHERE exam_id IN ({format_strings})", tuple(exam_ids))
        cursor.execute(f"DELETE FROM proctor_absence WHERE exam_id IN ({format_strings})", tuple(exam_ids))
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

        # Room conflict & Capacity check
        if new_room_id:
            cursor.execute("SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE room_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL", (new_room_id, exam_id))
            for row in cursor.fetchall():
                r_start = row['exam_date_time']
                if isinstance(r_start, str): r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
                r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
                if new_start < r_end and r_start < new_end:
                    conflicts.append(f"⚠️ Room conflict: room is already used by '{row['subject_name']}' at {r_start}")

            cursor.execute("SELECT room_name, capacity FROM rooms WHERE id = %s", (new_room_id,))
            rm_data = cursor.fetchone()
            if rm_data:
                cursor.execute("""
                    SELECT e.section, COALESCE(inst.capacity_default, 40) as inst_cap,
                           (SELECT COUNT(*) FROM users u WHERE u.role = 'student' AND u.section = e.section) as stu_cnt
                    FROM exams e
                    LEFT JOIN institutes inst ON e.institute_id = inst.id
                    WHERE e.id = %s
                """, (exam_id,))
                ex_info = cursor.fetchone() or {}
                needed_cap = ex_info.get('stu_cnt') or ex_info.get('inst_cap') or 40
                if rm_data.get('capacity', 0) < needed_cap:
                    conflicts.append(f"⚠️ Room Capacity Warning: Room '{rm_data['room_name']}' has only {rm_data['capacity']} seats, but section '{ex_info.get('section')}' requires at least {needed_cap} seats.")

        # Proctor/instructor conflict & Self-Proctoring Exclusion check
        if new_instructor_id:
            cursor.execute("SELECT subject_name, section, exam_date_time, duration_minutes FROM exams WHERE instructor_id=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL", (new_instructor_id, exam_id))
            for row in cursor.fetchall():
                r_start = row['exam_date_time']
                if isinstance(r_start, str): r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
                r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
                if new_start < r_end and r_start < new_end:
                    conflicts.append(f"⚠️ Instructor conflict: proctor is already assigned to '{row['subject_name']}' at {r_start}")

            import re
            cursor.execute("SELECT name, subjects_taught FROM instructors WHERE id = %s", (new_instructor_id,))
            inst_data = cursor.fetchone()
            if inst_data and inst_data.get('subjects_taught'):
                inst_subs = {s.strip().lower() for s in re.split(r'[,|;]', inst_data['subjects_taught']) if s.strip()}
                cursor.execute("SELECT subject_name FROM exams WHERE id = %s", (exam_id,))
                cur_ex = cursor.fetchone()
                if cur_ex and cur_ex.get('subject_name'):
                    s_name = cur_ex['subject_name'].strip().lower()
                    if s_name in inst_subs or any(s_name == sub or sub in s_name for sub in inst_subs):
                        conflicts.append(f"⚠️ Academic Integrity Rule: Instructor '{inst_data['name']}' teaches '{cur_ex.get('subject_name')}' and is strictly prohibited from proctoring their own course.")





        # Subject conflict: check if sister sections are scheduled at different times
        cursor.execute("SELECT subject_name FROM exams WHERE id=%s", (exam_id,))
        sub_row = cursor.fetchone()
        if sub_row and sub_row.get('subject_name'):
            subj_name = sub_row['subject_name'].strip().lower()
            if subj_name:
                cursor.execute(
                    "SELECT section, exam_date_time FROM exams WHERE LOWER(TRIM(subject_name))=%s AND id!=%s AND status='Scheduled' AND exam_date_time IS NOT NULL",
                    (subj_name, exam_id)
                )
                for row in cursor.fetchall():
                    s_time = row['exam_date_time']
                    if isinstance(s_time, str): s_time = _dt.strptime(s_time, '%Y-%m-%d %H:%M:%S')
                    # We just check if the new_start is exactly the same as the sister section
                    if new_start != s_time:
                        conflicts.append(f"? Integrity Risk: Section '{row['section']}' is taking this exam at {s_time}. (Use 'Sync ALL' to avoid this).")
                        # Only add this conflict warning once to avoid spam
                        break

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

def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str, sync_all=False, form_data=None):
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

        cursor_r.execute(
            "SELECT subject_name, section, instructor_id, room_id, exam_date_time FROM exams WHERE id=%s",
            (exam_id,)
        )
        old = cursor_r.fetchone() or {}
        old_instructor_id = old.get('instructor_id')
        section  = (old.get('section') or '').strip()
        subject  = old.get('subject_name') or 'Exam'
        dt_str   = new_dt.strftime('%b %d, %Y %I:%M %p')

        sister_ids = []
        if sync_all and subject:
            cursor_r.execute("SELECT id FROM exams WHERE UPPER(REPLACE(subject_name,' ',''))=UPPER(REPLACE(%s,' ','')) AND id!=%s", (subject, exam_id))
            sister_ids = [r['id'] for r in cursor_r.fetchall()]

        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, instructor_name=(SELECT name FROM instructors WHERE id=%s), exam_date_time=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_instructor_id, new_dt, exam_id)
        )
        
        if sync_all and sister_ids:
            for sid in sister_ids:
                s_room = form_data.get(f'sister_room_{sid}') if form_data else None
                s_inst = form_data.get(f'sister_inst_{sid}') if form_data else None
                if s_room and s_inst:
                    cursor.execute(
                        "UPDATE exams SET exam_date_time=%s, room_id=%s, instructor_id=%s, status='Scheduled' WHERE id=%s",
                        (new_dt, s_room, s_inst, sid)
                    )
                else:
                    cursor.execute(
                        "UPDATE exams SET exam_date_time=%s, status='Scheduled' WHERE id=%s",
                        (new_dt, sid)
                    )
        db.commit()

        # Only notify proctors and students about manual schedule edits if the schedule is already published!
        if is_schedule_published():
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

def get_public_timetable(section=None, institute_id=None, bypass_published_guard=False):
    # Protect draft schedules from unauthenticated public leakage
    if not bypass_published_guard and not is_schedule_published():
        return []
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
              AND TRIM(e.section) = %s
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

def get_all_sections():
    """
    Returns a sorted list of all unique class sections in the system
    (derived from both users and examination allocations).
    """
    db = open_db()
    if not db: return []
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT DISTINCT section FROM (
                SELECT section FROM users WHERE section IS NOT NULL AND section != ''
                UNION
                SELECT section FROM exams WHERE section IS NOT NULL AND section != ''
            ) AS s ORDER BY section ASC
        """)
        return [r[0] for r in cur.fetchall() if r[0]]
    except Exception:
        return []
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
        cursor.execute(
            "INSERT INTO exam_settings (id, exam_term, exam_semester) VALUES (1, %s, %s) "
            "ON DUPLICATE KEY UPDATE exam_term=VALUES(exam_term), exam_semester=VALUES(exam_semester)",
            (exam_term, exam_semester)
        )
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
                d = str(entry.get('date', '')).strip()
                if not d: continue
                st = str(entry.get('start_time', '07:00')).strip() or '07:00'
                et = str(entry.get('end_time', '20:00')).strip() or '20:00'
                cursor.execute("INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                               (instructor_id, d, st, et))
            else:
                d = str(entry).strip()
                if not d: continue
                cursor.execute("INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, '07:00', '20:00')",
                               (instructor_id, d))
        db.commit()
    finally:
        db.close()

def bulk_save_proctor_availability(instructor_ids, entries, mode='replace'):
    """Save availability entries for multiple instructors.
       mode: 'replace' to overwrite all existing availability,
             'append' to keep existing and add new dates (updating times if date already present).
    """
    db = open_db()
    if not db or not instructor_ids: return
    try:
        cursor = db.cursor()
        valid_entries = []
        for e in entries:
            if isinstance(e, dict):
                d = str(e.get('date', '')).strip()
                if not d: continue
                st = str(e.get('start_time', '07:00')).strip() or '07:00'
                et = str(e.get('end_time', '20:00')).strip() or '20:00'
                valid_entries.append({'date': d, 'start_time': st, 'end_time': et})
            elif isinstance(e, str) and e.strip():
                valid_entries.append({'date': e.strip(), 'start_time': '07:00', 'end_time': '20:00'})

        for raw_id in instructor_ids:
            try:
                iid = int(raw_id)
            except (ValueError, TypeError):
                continue

            if mode == 'replace':
                cursor.execute("DELETE FROM proctor_availability WHERE instructor_id=%s", (iid,))
                for ve in valid_entries:
                    cursor.execute(
                        "INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                        (iid, ve['date'], ve['start_time'], ve['end_time'])
                    )
            elif mode == 'append':
                for ve in valid_entries:
                    cursor.execute("SELECT id FROM proctor_availability WHERE instructor_id=%s AND available_date=%s", (iid, ve['date']))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute("UPDATE proctor_availability SET start_time=%s, end_time=%s WHERE id=%s", (ve['start_time'], ve['end_time'], row[0]))
                    else:
                        cursor.execute("INSERT INTO proctor_availability (instructor_id, available_date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                                       (iid, ve['date'], ve['start_time'], ve['end_time']))
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
            SELECT e.id, e.subject_name, e.section, e.subject_type, s.code as subject_code,
                   e.exam_date_time, e.duration_minutes, e.status,
                   r.room_name, r.capacity,
                   COALESCE(dept_inst.code, 'N/A') as offering_institute_code,
                   COALESCE(dept_inst.name, 'Department') as offering_institute_name,
                   (SELECT COUNT(*) FROM proctor_absence pa WHERE pa.exam_id = e.id AND pa.instructor_id = %s) as is_absent_reported,
                   (SELECT pa.reason FROM proctor_absence pa WHERE pa.exam_id = e.id AND pa.instructor_id = %s ORDER BY pa.id DESC LIMIT 1) as absence_reason,
                   (SELECT COUNT(*) FROM relievers rel WHERE rel.exam_id = e.id) as has_reliever,
                   (SELECT inst.name FROM relievers rel LEFT JOIN instructors inst ON rel.instructor_id = inst.id WHERE rel.exam_id = e.id ORDER BY rel.id DESC LIMIT 1) as reliever_name,
                   (SELECT COUNT(*) FROM relievers rel WHERE rel.exam_id = e.id AND rel.instructor_id = %s) as is_assigned_reliever
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN subjects s ON e.subject_id = s.id
            LEFT JOIN institutes dept_inst ON dept_inst.id = COALESCE(e.institute_id, s.institute_id)
            WHERE (e.instructor_id = %s OR e.id IN (SELECT exam_id FROM proctor_absence WHERE instructor_id = %s))
              AND e.status = 'Scheduled'
              AND e.exam_date_time IS NOT NULL
            ORDER BY e.exam_date_time ASC, e.section ASC
        """, (instructor_id, instructor_id, instructor_id, instructor_id, instructor_id))
        rows = cursor.fetchall()
        for r in rows:
            inst_code = (r.get('offering_institute_code') or '').strip()
            if inst_code and inst_code != 'N/A':
                r['claim_office'] = f"{inst_code} Dean's / Secretary Office"
            else:
                r['claim_office'] = "Department Secretary Office"
        return rows
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
                SELECT e.id as exam_id, e.subject_name, e.section, e.exam_date_time, e.duration_minutes,
                       e.instructor_id, e.instructor_name, r.room_name,
                       e.institute_id,
                       c.collected_by_instructor_id, c.collected_at, c.returned_at, c.notes,
                       inst.name as institute_name
                FROM exams e
                LEFT JOIN exam_collection c ON e.id = c.exam_id
                LEFT JOIN institutes inst ON e.institute_id = inst.id
                LEFT JOIN rooms r ON e.room_id = r.id
                WHERE e.status = 'Scheduled' AND e.institute_id = %s
                ORDER BY e.exam_date_time ASC
            """, (institute_id,))
        else:
            cursor.execute("""
                SELECT e.id as exam_id, e.subject_name, e.section, e.exam_date_time, e.duration_minutes,
                       e.instructor_id, e.instructor_name, r.room_name,
                       e.institute_id,
                       c.collected_by_instructor_id, c.collected_at, c.returned_at, c.notes,
                       inst.name as institute_name
                FROM exams e
                LEFT JOIN exam_collection c ON e.id = c.exam_id
                LEFT JOIN institutes inst ON e.institute_id = inst.id
                LEFT JOIN rooms r ON e.room_id = r.id
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
        valid_instructor_id = None
        if collected_by_instructor_id:
            try:
                candidate_id = int(collected_by_instructor_id)
                cursor.execute("SELECT id FROM instructors WHERE id = %s", (candidate_id,))
                if cursor.fetchone():
                    valid_instructor_id = candidate_id
            except (ValueError, TypeError):
                valid_instructor_id = None
        
        # If no instructor specified, fall back to the exam's assigned instructor if available
        if not valid_instructor_id:
            cursor.execute("SELECT instructor_id FROM exams WHERE id = %s", (exam_id,))
            row = cursor.fetchone()
            if row and row[0]:
                valid_instructor_id = row[0]

        cursor.execute("""
            INSERT INTO exam_collection (exam_id, collected_by_instructor_id, collected_at, notes)
            VALUES (%s, %s, NOW(), %s)
            ON DUPLICATE KEY UPDATE
                collected_by_instructor_id = VALUES(collected_by_instructor_id),
                collected_at = NOW(),
                notes = VALUES(notes)
        """, (exam_id, valid_instructor_id, notes))
        db.commit()
    finally:
        db.close()

def mark_exam_returned(exam_id, notes=''):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO exam_collection (exam_id, returned_at, notes)
            VALUES (%s, NOW(), %s)
            ON DUPLICATE KEY UPDATE
                returned_at = NOW(),
                notes = CONCAT(IFNULL(notes,''), '\n', VALUES(notes))
        """, (exam_id, notes))
        db.commit()
    finally:
        db.close()

def get_collection_stats(institute_id=None):
    db = open_db()
    if not db: return {'total': 0, 'collected': 0, 'returned': 0, 'pending_collection': 0}
    try:
        cursor = db.cursor(dictionary=True)
        if institute_id:
            cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND institute_id=%s", (institute_id,))
            total = cursor.fetchone()['c'] or 0
            if total == 0:
                return {'total': 0, 'collected': 0, 'returned': 0, 'pending_collection': 0}
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.collected_at IS NOT NULL AND e.status='Scheduled' AND e.exam_date_time IS NOT NULL AND e.institute_id=%s
            """, (institute_id,))
            collected = cursor.fetchone()['c'] or 0
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.returned_at IS NOT NULL AND e.status='Scheduled' AND e.exam_date_time IS NOT NULL AND e.institute_id=%s
            """, (institute_id,))
            returned = cursor.fetchone()['c'] or 0
        else:
            cursor.execute("SELECT COUNT(*) as c FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL")
            total = cursor.fetchone()['c'] or 0
            if total == 0:
                return {'total': 0, 'collected': 0, 'returned': 0, 'pending_collection': 0}
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.collected_at IS NOT NULL AND e.status='Scheduled' AND e.exam_date_time IS NOT NULL
            """)
            collected = cursor.fetchone()['c'] or 0
            cursor.execute("""
                SELECT COUNT(*) as c FROM exam_collection ec
                JOIN exams e ON ec.exam_id = e.id
                WHERE ec.returned_at IS NOT NULL AND e.status='Scheduled' AND e.exam_date_time IS NOT NULL
            """)
            returned = cursor.fetchone()['c'] or 0
        pending = max(0, total - collected)
        return {'total': total, 'collected': collected, 'returned': returned, 'pending_collection': pending}
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
            SELECT p.*, i.name as instructor_name, e.subject_name, e.section, e.exam_date_time, e.duration_minutes, u.full_name as reported_by
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

def clear_absence_reports():
    db = open_db()
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM proctor_absence")
        db.commit()
        return True
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

def clear_all_notifications(user_id):
    db = open_db()
    if not db: return False
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM notifications WHERE user_id=%s", (user_id,))
        db.commit()
        return True
    finally:
        db.close()

def delete_selected_notifications(user_id, notif_ids):
    """Deletes only the specified notification IDs belonging to user_id."""
    if not notif_ids:
        return 0
    clean_ids = []
    for nid in notif_ids:
        try:
            clean_ids.append(int(nid))
        except (ValueError, TypeError):
            continue
    if not clean_ids:
        return 0
    db = open_db()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        placeholders = ",".join(["%s"] * len(clean_ids))
        cursor.execute(
            f"DELETE FROM notifications WHERE user_id = %s AND id IN ({placeholders})",
            tuple([user_id] + clean_ids)
        )
        deleted = cursor.rowcount
        db.commit()
        return deleted
    finally:
        db.close()

def get_notifications(user_id, unread_only=False):
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        # If schedule is currently in Draft mode (not published), purge any premature assignment notifications
        cursor.execute("SELECT schedule_published FROM system_settings WHERE id = 1")
        st = cursor.fetchone()
        if st and not st.get('schedule_published'):
            cursor.execute("""
                DELETE FROM notifications
                WHERE title LIKE '%Proctoring Assignment:%'
                   OR title LIKE '%Exam Scheduled:%'
                   OR title = 'Exam Timetable Published'
            """)
            db.commit()
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
        cursor.execute("SELECT schedule_published FROM system_settings WHERE id = 1")
        st = cursor.fetchone()
        if st and not st.get('schedule_published'):
            cursor.execute("""
                DELETE FROM notifications
                WHERE title LIKE '%Proctoring Assignment:%'
                   OR title LIKE '%Exam Scheduled:%'
                   OR title = 'Exam Timetable Published'
            """)
            db.commit()
        cursor.execute("SELECT COUNT(*) as c FROM notifications WHERE user_id=%s AND is_read=0", (user_id,))
        return cursor.fetchone()['c']
    finally:
        db.close()

def get_live_sync_signature():
    """
    Returns a compact state signature for real-time auto-refresh across portals:
    tracks schedule publication status, proctor absence reports, substitute relievers, and exam collection.
    """
    db = open_db()
    if not db:
        return ""
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT schedule_published, schedule_published_at FROM system_settings WHERE id = 1")
        st = cursor.fetchone() or {}
        pub = int(bool(st.get('schedule_published', 0)))
        pub_at = str(st.get('schedule_published_at') or '')

        cursor.execute("SELECT COUNT(*) AS cnt, COALESCE(MAX(id), 0) AS max_id FROM proctor_absence")
        ab = cursor.fetchone() or {}

        cursor.execute("SELECT COUNT(*) AS cnt, COALESCE(MAX(id), 0) AS max_id FROM relievers")
        rl = cursor.fetchone() or {}

        cursor.execute("SELECT COUNT(*) AS cnt, COALESCE(MAX(collected_at), '') AS max_col, COALESCE(MAX(returned_at), '') AS max_ret FROM exam_collection")
        ec = cursor.fetchone() or {}

        return f"pub:{pub}:{pub_at}|ab:{ab.get('cnt',0)}:{ab.get('max_id',0)}|rl:{rl.get('cnt',0)}:{rl.get('max_id',0)}|ec:{ec.get('cnt',0)}:{ec.get('max_col','')}:{ec.get('max_ret','')}"
    except Exception:
        return ""
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
                               (row.get('name'), row.get('code'), institute_id, row.get('is_common', 0), int(row.get('content_group')) if (row.get('content_group') is not None and str(row.get('content_group')).strip().isdigit()) else None))
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


def get_suggested_times(exam_id, duration_minutes, room_id=0, proctor_id=0):
    from datetime import datetime as _dt, timedelta as _td, date as _date, time as _time
    db_conn = open_db()
    if not db_conn: return []
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Get section for this exam
        cursor.execute("SELECT section, subject_type FROM exams WHERE id=%s", (exam_id,))
        this_exam = cursor.fetchone()
        section = this_exam['section'].strip() if this_exam and this_exam.get('section') else None
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major' if this_exam else True

        # Find the earliest scheduled exam to know when "Exam Week" is, or use today
        cursor.execute("SELECT MIN(exam_date_time) as min_dt FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL")
        min_row = cursor.fetchone()
        if min_row and min_row['min_dt']:
            start_date = min_row['min_dt']
            if isinstance(start_date, str):
                start_date = _dt.strptime(start_date, '%Y-%m-%d %H:%M:%S').date()
            else:
                start_date = start_date.date()
        else:
            start_date = _dt.today().date()
            
        if start_date < _dt.today().date():
            start_date = _dt.today().date()

        suggestions = []
        days_to_scan = 14
        
        # We need check_edit_conflicts function logic, but we can't easily call it in a loop without hitting the DB 100 times.
        # Let's fetch all scheduled exams ONCE into memory to make scanning ultra-fast!
        cursor.execute("SELECT id, section, room_id, instructor_id, exam_date_time, duration_minutes, subject_type FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s", (exam_id,))
        all_exams = cursor.fetchall()
        for ex in all_exams:
            if isinstance(ex['exam_date_time'], str):
                ex['exam_date_time'] = _dt.strptime(ex['exam_date_time'], '%Y-%m-%d %H:%M:%S')
                
        # Also get proctor availability if a proctor is specified
        proctor_avail = get_proctor_availability()

        for day_offset in range(days_to_scan):
            current_date = start_date + _td(days=day_offset)
            # Skip Sundays
            if current_date.weekday() == 6: continue
            
            # Scan from 7 AM to 5 PM
            for hour in range(7, 18):
                # We will check top of the hour and half past
                for minute in (0, 30):
                    slot_start = _dt.combine(current_date, _time(hour, minute))
                    slot_end = slot_start + _td(minutes=duration_minutes)
                    
                    if slot_end.time() > _time(20, 0): # Don't go past 8 PM
                        continue
                        
                    conflict = False
                    day_major = 0
                    day_minor = 0
                    
                    for ex in all_exams:
                        ex_start = ex['exam_date_time']
                        ex_end = ex_start + _td(minutes=ex['duration_minutes'] or 60)
                        
                        # 1. Section conflict
                        my_sections = []
                        if section: my_sections.append(section)
                        if ex['section'] and ex['section'] in my_sections:
                            # Time overlap with 1 hr break
                            buf_start = slot_start - _td(hours=1)
                            buf_end = slot_end + _td(hours=1)
                            if buf_start < ex_end and ex_start < buf_end:
                                conflict = True
                                break
                            # Daily limits
                            if ex_start.date() == current_date:
                                if (ex.get('subject_type') or 'Major') == 'Major': day_major += 1
                                else: day_minor += 1
                        
                        # 2. Room conflict
                        if room_id and ex['room_id'] == room_id:
                            if slot_start < ex_end and ex_start < slot_end:
                                conflict = True
                                break
                                
                        # 3. Proctor conflict
                        if proctor_id and ex['instructor_id'] == proctor_id:
                            if slot_start < ex_end and ex_start < slot_end:
                                conflict = True
                                break
                                
                    if conflict: continue
                    
                    # Section daily limits
                    if section:
                        minor_limit = 4 - day_major
                        if is_major and day_major >= 3: conflict = True
                        if not is_major and day_minor >= minor_limit: conflict = True
                        if day_major + day_minor >= 3: conflict = True
                    if conflict: continue
                    
                    # 4. Proctor Availability explicitly declared
                    if proctor_id:
                        avail_entries = proctor_avail.get(proctor_id)
                        if avail_entries:
                            has_entry = False
                            time_match = False
                            for ent in avail_entries:
                                if ent['date'] == current_date:
                                    has_entry = True
                                    if slot_start.time() >= ent['start_time'] and slot_end.time() <= ent['end_time']:
                                        time_match = True
                                        break
                            if has_entry and not time_match:
                                conflict = True
                    if conflict: continue
                    
                    # It's a valid slot!
                    suggestions.append({
                        'datetime': slot_start.strftime('%Y-%m-%dT%H:%M'),
                        'label': slot_start.strftime('%a, %b %d, %Y - %I:%M %p')
                    })
                    
                    # Only return up to 10 suggestions to avoid overwhelming the UI
                    if len(suggestions) >= 10:
                        return suggestions
                        
        return suggestions
    finally:
        db_conn.close()


def get_full_auto_schedule(exam_id, duration_minutes, sync_all=False):
    from datetime import datetime as _dt, timedelta as _td, date as _date, time as _time
    import random
    db_conn = open_db()
    if not db_conn: return None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Get section for this exam
        cursor.execute("SELECT subject_name, section, subject_type, institute_id FROM exams WHERE id=%s", (exam_id,))
        this_exam = cursor.fetchone()
        if not this_exam: return None
        
        section = this_exam['section'].strip() if this_exam.get('section') else None
        subject_name = this_exam['subject_name']
        is_major = (this_exam.get('subject_type') or 'Major') == 'Major'
        institute_id = this_exam.get('institute_id')
        
        sister_sections = []
        if sync_all and subject_name:
            cursor.execute("SELECT id, section FROM exams WHERE UPPER(REPLACE(subject_name,' ',''))=UPPER(REPLACE(%s,' ','')) AND id!=%s", (subject_name, exam_id))
            sister_sections = cursor.fetchall()
        
        total_sections_needed = 1 + len(sister_sections)

        # Find the start date
        cursor.execute("SELECT MIN(exam_date_time) as min_dt FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL")
        min_row = cursor.fetchone()
        if min_row and min_row['min_dt']:
            start_date = min_row['min_dt']
            if isinstance(start_date, str):
                start_date = _dt.strptime(start_date, '%Y-%m-%d %H:%M:%S').date()
            else:
                start_date = start_date.date()
        else:
            start_date = _dt.today().date()
            
        if start_date < _dt.today().date():
            start_date = _dt.today().date()

        days_to_scan = 14
        
        # Load all exams
        cursor.execute("SELECT id, section, room_id, instructor_id, exam_date_time, duration_minutes, subject_type FROM exams WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s", (exam_id,))
        all_exams = cursor.fetchall()
        for ex in all_exams:
            if isinstance(ex['exam_date_time'], str):
                ex['exam_date_time'] = _dt.strptime(ex['exam_date_time'], '%Y-%m-%d %H:%M:%S')
                
        # Load all rooms and proctors
        cursor.execute("SELECT id, room_name, capacity FROM rooms ORDER BY room_name")
        all_rooms = cursor.fetchall()
        
        # Prefer proctors from the same institute if possible, but load all
        cursor.execute("SELECT id, name, institute_id FROM instructors WHERE status='Active' ORDER BY name")
        all_insts = cursor.fetchall()
        
        proctor_avail = get_proctor_availability()

        for day_offset in range(days_to_scan):
            current_date = start_date + _td(days=day_offset)
            if current_date.weekday() == 6: continue # skip Sunday
            
            for hour in range(7, 18):
                for minute in (0, 30):
                    slot_start = _dt.combine(current_date, _time(hour, minute))
                    slot_end = slot_start + _td(minutes=duration_minutes)
                    
                    if slot_end.time() > _time(20, 0): continue
                        
                    section_conflict = False
                    day_major = 0
                    day_minor = 0
                    
                    busy_rooms = set()
                    busy_insts = set()
                    
                    for ex in all_exams:
                        ex_start = ex['exam_date_time']
                        ex_end = ex_start + _td(minutes=ex['duration_minutes'] or 60)
                        
                        # Time overlap checks
                        buf_start = slot_start - _td(hours=1)
                        buf_end = slot_end + _td(hours=1)
                        
                        overlap_strict = (slot_start < ex_end and ex_start < slot_end)
                        overlap_buffer = (buf_start < ex_end and ex_start < buf_end)
                        
                        my_sections = []
                        if section: my_sections.append(section)
                        my_sections.extend([s['section'] for s in sister_sections if s['section']])
                        
                        if ex['section'] and ex['section'] in my_sections:
                            if overlap_buffer:
                                section_conflict = True
                                break
                            if ex_start.date() == current_date:
                                if (ex.get('subject_type') or 'Major') == 'Major': day_major += 1
                                else: day_minor += 1
                                
                        if overlap_strict:
                            if ex['room_id']: busy_rooms.add(ex['room_id'])
                            if ex['instructor_id']: busy_insts.add(ex['instructor_id'])
                                
                    if section_conflict: continue
                    
                    if section:
                        minor_limit = 4 - day_major
                        if is_major and day_major >= 3: continue
                        if not is_major and day_minor >= minor_limit: continue
                        if day_major + day_minor >= 3: continue
                    
                    # Find a free room
                    free_rooms = [r for r in all_rooms if r['id'] not in busy_rooms]
                    if not free_rooms: continue
                    
                    # Find a free proctor
                    free_insts = []
                    for i in all_insts:
                        if i['id'] in busy_insts: continue
                        
                        # Check explicitly declared availability
                        avail_entries = proctor_avail.get(i['id'])
                        if avail_entries:
                            has_entry = False
                            time_match = False
                            for ent in avail_entries:
                                if ent['date'] == current_date:
                                    has_entry = True
                                    if slot_start.time() >= ent['start_time'] and slot_end.time() <= ent['end_time']:
                                        time_match = True
                                        break
                            if has_entry and not time_match:
                                continue # declared unavailable
                        
                        free_insts.append(i)
                        
                    if len(free_insts) < total_sections_needed or len(free_rooms) < total_sections_needed: continue
                    
                    # We found a slot!
                    # Pick a room (just the first available one, or random to distribute load)
                    chosen_room = random.choice(free_rooms)['id']
                    
                    # Pick a proctor (prefer same institute)
                    same_inst = [i for i in free_insts if i['institute_id'] == institute_id]
                    if same_inst:
                        chosen_proctor = random.choice(same_inst)['id']
                    else:
                        chosen_proctor = random.choice(free_insts)['id']
                        
                    return {
                        'datetime': slot_start.strftime('%Y-%m-%dT%H:%M'),
                        'room_id': chosen_room,
                        'instructor_id': chosen_proctor
                    }
                    
        return None
    finally:
        db_conn.close()

def get_resource_schedule_details(resource_type, resource_id):
    """
    Returns complete availability & scheduled slots for an instructor or room.
    resource_type: 'instructor' or 'room'
    resource_id: int
    """
    from datetime import datetime as _dt, date as _date, time as _time, timedelta as _td
    from collections import defaultdict
    db = open_db()
    if not db: return None

    try:
        cursor = db.cursor(dictionary=True)

        # 1. Fetch resource metadata
        if resource_type == 'instructor':
            cursor.execute("""
                SELECT i.*, inst.name as institute_name
                FROM instructors i
                LEFT JOIN institutes inst ON i.institute_id = inst.id
                WHERE i.id = %s
            """, (resource_id,))
            resource = cursor.fetchone()
            if not resource: return None
            resource_name = resource['name']
        elif resource_type == 'room':
            cursor.execute("""
                SELECT r.*, inst.name as institute_name
                FROM rooms r
                LEFT JOIN institutes inst ON r.institute_id = inst.id
                WHERE r.id = %s
            """, (resource_id,))
            resource = cursor.fetchone()
            if not resource: return None
            resource_name = resource['room_name']
        else:
            return None

        # 2. System settings & exam period
        settings = get_system_settings() or {}
        period_start, period_end = get_exam_period()

        def _parse_time(val, default):
            if isinstance(val, _td):
                return (_dt.min + val).time()
            if isinstance(val, _time):
                return val
            if isinstance(val, str):
                parts = val.split(':')
                if len(parts) >= 2:
                    return _time(int(parts[0]), int(parts[1]))
            return default

        day_start = _parse_time(settings.get('day_start'), _time(7, 0))
        day_end   = _parse_time(settings.get('day_end'), _time(20, 0))
        max_daily_hrs = float(settings.get('max_daily_proctor_hrs') or 4.0)

        # 3. Scheduled exams for this resource
        if resource_type == 'instructor':
            cursor.execute("""
                SELECT e.id, e.subject_name, e.section, e.exam_date_time, e.duration_minutes, e.subject_type,
                       r.room_name as other_name, r.building as other_building
                FROM exams e
                LEFT JOIN rooms r ON e.room_id = r.id
                WHERE e.instructor_id = %s AND e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
                ORDER BY e.exam_date_time
            """, (resource_id,))
        else:
            cursor.execute("""
                SELECT e.id, e.subject_name, e.section, e.exam_date_time, e.duration_minutes, e.subject_type,
                       i.name as other_name, i.building as other_building
                FROM exams e
                LEFT JOIN instructors i ON e.instructor_id = i.id
                WHERE e.room_id = %s AND e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
                ORDER BY e.exam_date_time
            """, (resource_id,))

        raw_exams = cursor.fetchall()

        # Proctor working availability (if instructor)
        avail_by_date = {}
        if resource_type == 'instructor':
            cursor.execute("""
                SELECT available_date, start_time, end_time
                FROM proctor_availability
                WHERE instructor_id = %s
            """, (resource_id,))
            for r in cursor.fetchall():
                d = r['available_date']
                if not isinstance(d, _date):
                    d = _date.fromisoformat(str(d))
                st = _parse_time(r['start_time'], day_start)
                et = _parse_time(r['end_time'], day_end)
                avail_by_date[d] = {'start': st, 'end': et}

        # Determine target dates
        target_dates = []
        if period_start and period_end:
            cur_d = period_start
            while cur_d <= period_end:
                if cur_d.weekday() != 6:  # Skip Sunday
                    target_dates.append(cur_d)
                cur_d += _td(days=1)
        
        # If no period, or exams fall outside, include exam dates
        exam_dates_set = set()
        for e in raw_exams:
            edt = e['exam_date_time']
            if isinstance(edt, str):
                try: edt = _dt.strptime(edt, '%Y-%m-%d %H:%M:%S')
                except ValueError: edt = _dt.strptime(edt, '%Y-%m-%dT%H:%M')
            exam_dates_set.add(edt.date())

        for ed in sorted(exam_dates_set):
            if ed not in target_dates:
                target_dates.append(ed)
        target_dates.sort()

        if not target_dates:
            today = _date.today()
            target_dates = [today + _td(days=i) for i in range(5) if (today + _td(days=i)).weekday() != 6]

        # Group exams by date
        exams_by_date = defaultdict(list)
        for e in raw_exams:
            edt = e['exam_date_time']
            if isinstance(edt, str):
                try: edt = _dt.strptime(edt, '%Y-%m-%d %H:%M:%S')
                except ValueError: edt = _dt.strptime(edt, '%Y-%m-%dT%H:%M')
            dur = e['duration_minutes'] or 60
            end_dt = edt + _td(minutes=dur)
            exams_by_date[edt.date()].append({
                'id': e['id'],
                'subject_name': e['subject_name'] or 'Unknown Subject',
                'section': e['section'] or '',
                'subject_type': e.get('subject_type', 'Major'),
                'other_name': e.get('other_name') or 'Not Assigned',
                'start_dt': edt,
                'end_dt': end_dt,
                'start_time': edt.strftime('%I:%M %p'),
                'end_time': end_dt.strftime('%I:%M %p'),
                'duration_minutes': dur,
                'duration_hours': round(dur / 60.0, 1)
            })

        # Calculate free and busy slots per day
        days_result = []
        total_busy_hours = 0.0

        for d in target_dates:
            day_exams = sorted(exams_by_date[d], key=lambda x: x['start_dt'])
            
            # Determine daily work window
            if resource_type == 'instructor' and d in avail_by_date:
                w_start = avail_by_date[d]['start']
                w_end   = avail_by_date[d]['end']
                custom_avail = True
            else:
                w_start = day_start
                w_end   = day_end
                custom_avail = False

            w_start_dt = _dt.combine(d, w_start)
            w_end_dt   = _dt.combine(d, w_end)

            busy_slots = []
            day_busy_mins = 0

            for ex in day_exams:
                day_busy_mins += ex['duration_minutes']
                busy_slots.append({
                    'exam_id': ex['id'],
                    'subject_name': ex['subject_name'],
                    'section': ex['section'],
                    'subject_type': ex['subject_type'],
                    'other_name': ex['other_name'],
                    'start_time': ex['start_time'],
                    'end_time': ex['end_time'],
                    'duration_hours': ex['duration_hours']
                })

            # Calculate free intervals within work window
            free_slots = []
            curr_ptr = w_start_dt

            for ex in day_exams:
                if curr_ptr < ex['start_dt']:
                    free_mins = int((ex['start_dt'] - curr_ptr).total_seconds() / 60)
                    if free_mins >= 15:
                        free_slots.append({
                            'start_time': curr_ptr.strftime('%I:%M %p'),
                            'end_time': ex['start_dt'].strftime('%I:%M %p'),
                            'duration_hours': round(free_mins / 60.0, 1),
                            'duration_minutes': free_mins
                        })
                if ex['end_dt'] > curr_ptr:
                    curr_ptr = ex['end_dt']

            if curr_ptr < w_end_dt:
                free_mins = int((w_end_dt - curr_ptr).total_seconds() / 60)
                if free_mins >= 15:
                    free_slots.append({
                        'start_time': curr_ptr.strftime('%I:%M %p'),
                        'end_time': w_end_dt.strftime('%I:%M %p'),
                        'duration_hours': round(free_mins / 60.0, 1),
                        'duration_minutes': free_mins
                    })

            day_busy_hours = round(day_busy_mins / 60.0, 1)
            total_busy_hours += day_busy_hours

            days_result.append({
                'date': d.strftime('%Y-%m-%d'),
                'date_label': d.strftime('%a, %b %d, %Y'),
                'day_name': d.strftime('%A'),
                'is_completely_free': len(busy_slots) == 0,
                'custom_avail': custom_avail,
                'work_window': f"{w_start.strftime('%I:%M %p')} - {w_end.strftime('%I:%M %p')}",
                'busy_hours': day_busy_hours,
                'max_daily_hours': max_daily_hrs if resource_type == 'instructor' else None,
                'busy_slots': busy_slots,
                'free_slots': free_slots
            })

        return {
            'success': True,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'resource_name': resource_name,
            'info': resource,
            'total_exams': len(raw_exams),
            'total_busy_hours': round(total_busy_hours, 1),
            'days': days_result
        }
    finally:
        db.close()

def get_unresolved_absences(institute_id=None):
    """
    Returns pending/unresolved proctor absences for a given institute (or all if None).
    Matches if either the proctor belongs to the institute OR the exam belongs to the institute.
    Deduplicates multiple reports for the same exam.
    """
    db = open_db()
    if not db: return []
    try:
        cursor = db.cursor(dictionary=True)
        if institute_id:
            cursor.execute("""
                SELECT p.id, p.instructor_id, p.exam_id, p.reason, p.reported_by, p.reported_at,
                       i.name as instructor_name, e.subject_name, e.section, e.exam_date_time, e.institute_id,
                       e.duration_minutes, e.room_id, r.room_name, u.full_name as reported_by_name,
                       (SELECT COUNT(*) FROM relievers rel WHERE rel.exam_id = p.exam_id) as reliever_count
                FROM proctor_absence p
                INNER JOIN (
                    SELECT exam_id, MAX(id) as max_id
                    FROM proctor_absence
                    GROUP BY exam_id
                ) latest ON p.id = latest.max_id
                LEFT JOIN instructors i ON p.instructor_id = i.id
                LEFT JOIN exams e ON p.exam_id = e.id
                LEFT JOIN rooms r ON e.room_id = r.id
                LEFT JOIN users u ON p.reported_by = u.id
                WHERE (i.institute_id = %s OR e.institute_id = %s)
                HAVING reliever_count = 0
                ORDER BY p.reported_at DESC
            """, (institute_id, institute_id))
        else:
            cursor.execute("""
                SELECT p.id, p.instructor_id, p.exam_id, p.reason, p.reported_by, p.reported_at,
                       i.name as instructor_name, e.subject_name, e.section, e.exam_date_time, e.institute_id,
                       e.duration_minutes, e.room_id, r.room_name, u.full_name as reported_by_name,
                       (SELECT COUNT(*) FROM relievers rel WHERE rel.exam_id = p.exam_id) as reliever_count
                FROM proctor_absence p
                INNER JOIN (
                    SELECT exam_id, MAX(id) as max_id
                    FROM proctor_absence
                    GROUP BY exam_id
                ) latest ON p.id = latest.max_id
                LEFT JOIN instructors i ON p.instructor_id = i.id
                LEFT JOIN exams e ON p.exam_id = e.id
                LEFT JOIN rooms r ON e.room_id = r.id
                LEFT JOIN users u ON p.reported_by = u.id
                HAVING reliever_count = 0
                ORDER BY p.reported_at DESC
            """)
        return cursor.fetchall()
    finally:
        db.close()

def get_substitute_candidates(exam_id, institute_id=None):
    """
    Returns available proctors (strictly filtered to institute if provided) and available rooms
    for an exam's specific time slot.
    """
    from datetime import datetime as _dt, timedelta as _td
    db = open_db()
    if not db: return None

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, r.building as room_building, i.name as current_instructor_name,
                   inst.name as institute_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            WHERE e.id = %s
        """, (exam_id,))
        exam = cursor.fetchone()
        if not exam: return None

        exam_dt = exam.get('exam_date_time')
        dur = exam.get('duration_minutes') or 60
        if isinstance(exam_dt, str):
            try: exam_dt = _dt.strptime(exam_dt, '%Y-%m-%d %H:%M:%S')
            except ValueError: exam_dt = _dt.strptime(exam_dt, '%Y-%m-%dT%H:%M')
        
        exam_end = exam_dt + _td(minutes=dur) if exam_dt else None

        filter_inst = institute_id or exam.get('institute_id')
        
        if filter_inst:
            cursor.execute("""
                SELECT i.*, inst.name as institute_name
                FROM instructors i
                LEFT JOIN institutes inst ON i.institute_id = inst.id
                WHERE i.status = 'Active' AND (i.institute_id = %s OR i.institute_id IS NULL)
                ORDER BY i.name
            """, (filter_inst,))
        else:
            cursor.execute("""
                SELECT i.*, inst.name as institute_name
                FROM instructors i
                LEFT JOIN institutes inst ON i.institute_id = inst.id
                WHERE i.status = 'Active'
                ORDER BY i.name
            """)
        instructors = cursor.fetchall()

        busy_instructor_ids = {}
        busy_room_ids = {}
        if exam_dt and exam_end:
            cursor.execute("""
                SELECT id, instructor_id, room_id, exam_date_time, duration_minutes, subject_name, section
                FROM exams
                WHERE status = 'Scheduled' AND exam_date_time IS NOT NULL AND id != %s
            """, (exam_id,))
            for other in cursor.fetchall():
                o_start = other['exam_date_time']
                if isinstance(o_start, str):
                    try: o_start = _dt.strptime(o_start, '%Y-%m-%d %H:%M:%S')
                    except ValueError: o_start = _dt.strptime(o_start, '%Y-%m-%dT%H:%M')
                o_end = o_start + _td(minutes=other['duration_minutes'] or 60)
                if exam_dt < o_end and o_start < exam_end:
                    if other['instructor_id']:
                        busy_instructor_ids[other['instructor_id']] = f"Busy with {other['subject_name']} ({other['section']})"
                    if other['room_id']:
                        busy_room_ids[other['room_id']] = f"Occupied by {other['subject_name']} ({other['section']})"

        proctor_avail = get_proctor_availability()

        candidate_instructors = []
        for i in instructors:
            if i['id'] == exam.get('instructor_id'):
                continue
            
            is_free = True
            conflict_reason = None

            if i['id'] in busy_instructor_ids:
                is_free = False
                conflict_reason = busy_instructor_ids[i['id']]

            if is_free and exam.get('subject_name'):
                subs = [s.strip().lower() for s in (i.get('subjects_taught') or '').split(',') if s.strip()]
                if exam['subject_name'].strip().lower() in subs:
                    is_free = False
                    conflict_reason = "Teaches this course (Integrity Rule)"

            if is_free and exam_dt and proctor_avail.get(i['id']):
                avail_entries = proctor_avail[i['id']]
                has_entry = False
                time_match = False
                for ent in avail_entries:
                    if ent['date'] == exam_dt.date():
                        has_entry = True
                        if exam_dt.time() >= ent['start_time'] and exam_end.time() <= ent['end_time']:
                            time_match = True
                            break
                if has_entry and not time_match:
                    is_free = False
                    conflict_reason = "Outside declared available shift"

            candidate_instructors.append({
                'id': i['id'],
                'name': i['name'],
                'institute_name': i.get('institute_name') or 'General',
                'is_free': is_free,
                'conflict_reason': conflict_reason
            })

        candidate_instructors.sort(key=lambda x: (0 if x['is_free'] else 1, x['name']))

        cursor.execute("""
            SELECT r.*, inst.name as institute_name
            FROM rooms r
            LEFT JOIN institutes inst ON r.institute_id = inst.id
            ORDER BY r.room_name
        """)
        rooms = cursor.fetchall()
        candidate_rooms = []
        for r in rooms:
            is_free = True
            conflict_reason = None
            if r['id'] in busy_room_ids:
                is_free = False
                conflict_reason = busy_room_ids[r['id']]
            candidate_rooms.append({
                'id': r['id'],
                'room_name': r['room_name'],
                'capacity': r['capacity'],
                'building': r.get('building') or 'Main Campus',
                'is_current': (r['id'] == exam.get('room_id')),
                'is_free': is_free,
                'conflict_reason': conflict_reason
            })
        candidate_rooms.sort(key=lambda x: (0 if x['is_current'] else (1 if x['is_free'] else 2), x['room_name']))

        # Format exam datetime for display
        dt_display = exam_dt.strftime('%b %d, %Y %I:%M %p') if exam_dt else 'Not scheduled'

        return {
            'success': True,
            'exam': {
                'id': exam['id'],
                'subject_name': exam['subject_name'],
                'section': exam['section'],
                'datetime_str': dt_display,
                'duration_minutes': dur,
                'duration_hours': round(dur / 60.0, 1),
                'room_id': exam.get('room_id'),
                'room_name': exam.get('room_name') or '—',
                'instructor_id': exam.get('instructor_id'),
                'instructor_name': exam.get('current_instructor_name') or '—',
                'institute_name': exam.get('institute_name') or 'General Department'
            },
            'instructors': candidate_instructors,
            'rooms': candidate_rooms,
            'institute_name': exam.get('institute_name') or 'Department'
        }
    finally:
        db.close()

def reassign_exam_proctor_room(exam_id, new_instructor_id, new_room_id=None, reason="", reassigned_by=None):
    """
    Substitutes an exam proctor (and optionally room), inserts into relievers audit table,
    and dispatches notifications.
    """
    db = open_db()
    if not db: return False, "Database connection failed"
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM exams WHERE id = %s", (exam_id,))
        exam = cursor.fetchone()
        if not exam: return False, "Exam not found"

        old_instructor_id = exam.get('instructor_id')
        old_room_id = exam.get('room_id')

        cursor.execute("SELECT name FROM instructors WHERE id = %s", (new_instructor_id,))
        inst = cursor.fetchone()
        if not inst: return False, "Selected substitute instructor not found"
        new_inst_name = inst['name']

        # 1. Insert into relievers audit table
        cursor.execute("""
            INSERT INTO relievers (exam_id, instructor_id, reason)
            VALUES (%s, %s, %s)
        """, (exam_id, new_instructor_id, reason))

        # 2. Update exams table
        if new_room_id and str(new_room_id) != str(old_room_id or ''):
            cursor.execute("""
                UPDATE exams
                SET instructor_id = %s, instructor_name = %s, room_id = %s
                WHERE id = %s
            """, (new_instructor_id, new_inst_name, new_room_id, exam_id))
        else:
            cursor.execute("""
                UPDATE exams
                SET instructor_id = %s, instructor_name = %s
                WHERE id = %s
            """, (new_instructor_id, new_inst_name, exam_id))

        # 3. Notification for new substitute proctor
        cursor.execute("SELECT id FROM users WHERE instructor_id = %s", (new_instructor_id,))
        reliever_user = cursor.fetchone()
        if reliever_user:
            notif_title = "Assigned as Proctor Reliever"
            notif_msg = f"You have been assigned as a substitute proctor for {exam.get('subject_name')} ({exam.get('section')}) on {exam.get('exam_date_time')}. Reason: {reason or 'Emergency reliever dispatch'}."
            cursor.execute("INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)",
                           (reliever_user['id'], notif_title, notif_msg))

        # 4. Notification for Admins
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        for adm in cursor.fetchall():
            cursor.execute("INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)",
                           (adm['id'], "Proctor Substitution Dispatched",
                            f"Substitute proctor {new_inst_name} was dispatched for {exam.get('subject_name')} ({exam.get('section')})."))

        # 5. Notification for original proctor
        if old_instructor_id and old_instructor_id != new_instructor_id:
            cursor.execute("SELECT id FROM users WHERE instructor_id = %s", (old_instructor_id,))
            orig_user = cursor.fetchone()
            if orig_user:
                cursor.execute("INSERT INTO notifications (user_id, title, message, created_at, is_read) VALUES (%s, %s, %s, NOW(), 0)",
                               (orig_user['id'], "Reliever Assigned for Your Duty",
                                f"Prof. {new_inst_name} has been assigned as your substitute reliever for {exam.get('subject_name')} ({exam.get('section')}). You have been excused from this duty."))

        db.commit()
        return True, f"Successfully assigned {new_inst_name} as substitute proctor."
    except Exception as e:
        return False, str(e)
    finally:
        db.close()


# ── EXAM ARCHIVES (HISTORICAL RECORDS) ──────────────────────────────────────

def create_exam_archive(academic_year, exam_term, exam_semester, archive_title=None, notes=None, user_id=None, user_name=None):
    """
    Captures an immutable snapshot of the current scheduled examinations along with
    proctors, rooms, sections, and dates, and stores it in exam_archives.
    """
    import json
    db = open_db()
    if not db:
        return False, "Database connection failed."
    try:
        cursor = db.cursor(dictionary=True)
        # Fetch all currently scheduled exams with full relational details
        cursor.execute("""
            SELECT e.id, e.subject_name, e.section, e.subject_type, e.duration_minutes,
                   e.exam_date_time, e.room_id, r.room_name, r.building, r.floor, r.capacity,
                   e.instructor_id, COALESCE(i.name, e.instructor_name) AS instructor_name,
                   e.institute_id, inst.name AS institute_name, inst.code AS institute_code,
                   s.code AS subject_code
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            LEFT JOIN institutes inst ON e.institute_id = inst.id
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
            ORDER BY e.exam_date_time, e.section, e.subject_name
        """)
        exams = cursor.fetchall()
        if not exams:
            return False, "No scheduled exams found to archive."

        proctors = set()
        sections = set()
        dates = []
        serializable_exams = []

        for ex in exams:
            dt = ex.get('exam_date_time')
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(dt, datetime) else str(dt or '')
            d_only = dt.strftime("%Y-%m-%d") if isinstance(dt, datetime) else dt_str[:10]
            if d_only:
                dates.append(d_only)

            if ex.get('instructor_name'):
                proctors.add(ex['instructor_name'])
            if ex.get('section'):
                sections.add(ex['section'].strip())

            item = dict(ex)
            item['exam_date_time'] = dt_str
            if isinstance(dt, datetime):
                item['formatted_date'] = dt.strftime("%A, %B %d, %Y")
                item['formatted_time'] = dt.strftime("%I:%M %p")
                end_dt = dt + timedelta(minutes=int(ex.get('duration_minutes') or 60))
                item['formatted_time_end'] = end_dt.strftime("%I:%M %p")
            else:
                item['formatted_date'] = ''
                item['formatted_time'] = ''
                item['formatted_time_end'] = ''
            serializable_exams.append(item)

        total_exams = len(serializable_exams)
        total_proctors = len(proctors)
        total_sections = len(sections)
        period_start = min(dates) if dates else None
        period_end = max(dates) if dates else None

        if not archive_title or not archive_title.strip():
            archive_title = f"A.Y. {academic_year} {exam_semester} {exam_term}"

        snapshot_json = json.dumps(serializable_exams)

        cursor.execute("""
            INSERT INTO exam_archives
            (academic_year, exam_term, exam_semester, archive_title, total_exams, total_proctors,
             total_sections, period_start, period_end, archived_at, archived_by, archived_by_name, notes, snapshot_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
        """, (academic_year, exam_term, exam_semester, archive_title, total_exams, total_proctors,
              total_sections, period_start, period_end, user_id, user_name, notes, snapshot_json))
        db.commit()
        archive_id = cursor.lastrowid
        return True, archive_id
    except Exception as e:
        return False, str(e)
    finally:
        db.close()

def get_exam_archives():
    """
    Returns high-level metadata for all stored exam archives.
    """
    db = open_db()
    if not db:
        return []
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, academic_year, exam_term, exam_semester, archive_title,
                   total_exams, total_proctors, total_sections, period_start, period_end,
                   archived_at, archived_by, archived_by_name, notes
            FROM exam_archives
            ORDER BY archived_at DESC, id DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching exam archives: {e}")
        return []
    finally:
        db.close()

def get_exam_archive_by_id(archive_id):
    """
    Returns a specific exam archive with its full parsed snapshot data.
    """
    import json
    db = open_db()
    if not db:
        return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM exam_archives WHERE id = %s", (archive_id,))
        row = cursor.fetchone()
        if not row:
            return None
        try:
            row['exams'] = json.loads(row.get('snapshot_data') or '[]')
        except Exception:
            row['exams'] = []
        return row
    except Exception as e:
        print(f"Error fetching archive {archive_id}: {e}")
        return None
    finally:
        db.close()

def delete_exam_archive(archive_id):
    """
    Permanently removes a historical archive record.
    """
    db = open_db()
    if not db:
        return False, "Database connection failed."
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM exam_archives WHERE id = %s", (archive_id,))
        db.commit()
        return True, "Archive deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        db.close()

def sync_archive_durations(archive_id=None):
    """
    Synchronizes duration_minutes and formatted_time_end of all exams in
    exam_archives snapshot_data to match active system_settings (major_duration_hrs, minor_duration_hrs).
    If archive_id is provided, only that archive is synced; otherwise all archives are synced.
    """
    import json
    from datetime import datetime, timedelta
    settings = get_system_settings() or {}
    major_min = int(round(float(settings.get('major_duration_hrs', 2.0) or 2.0) * 60))
    minor_min = int(round(float(settings.get('minor_duration_hrs', 1.0) or 1.0) * 60))

    db = open_db()
    if not db:
        return False, "Database connection failed."
    try:
        cur = db.cursor(dictionary=True)
        if archive_id:
            cur.execute("SELECT id, snapshot_data FROM exam_archives WHERE id=%s", (archive_id,))
        else:
            cur.execute("SELECT id, snapshot_data FROM exam_archives")
        rows = cur.fetchall()

        update_cur = db.cursor()
        updated_count = 0
        for row in rows:
            raw_snap = row.get('snapshot_data')
            if not raw_snap:
                continue
            try:
                data = json.loads(raw_snap)
            except Exception:
                continue
            modified = False
            for ex in data:
                st = ex.get('subject_type') or 'Major'
                new_dur = major_min if st == 'Major' else minor_min
                if ex.get('duration_minutes') != new_dur:
                    ex['duration_minutes'] = new_dur
                    modified = True

                # Recalculate formatted_time_end
                dt_str = ex.get('exam_date_time')
                if dt_str:
                    try:
                        dt = datetime.strptime(str(dt_str)[:19], "%Y-%m-%d %H:%M:%S")
                        end_dt = dt + timedelta(minutes=new_dur)
                        new_end_str = end_dt.strftime("%I:%M %p")
                        if ex.get('formatted_time_end') != new_end_str:
                            ex['formatted_time_end'] = new_end_str
                            modified = True
                    except Exception:
                        pass
            if modified:
                update_cur.execute(
                    "UPDATE exam_archives SET snapshot_data=%s WHERE id=%s",
                    (json.dumps(data), row['id'])
                )
                updated_count += 1
        db.commit()
        return True, f"Successfully synced durations for {updated_count} archive(s)."
    except Exception as e:
        return False, str(e)
    finally:
        db.close()



def audit_schedule_conflicts(db=None):
    """
    Scans the live database for any scheduling anomalies:
    - Room Double-Bookings
    - Proctor Double-Bookings
    - Section Collisions (student section taking 2 exams at once)
    - Subject Desynchronization (sister sections taking same subject at different times)
    - Section 1-Hour Break Buffer Violations (<1 hour between exams)
    - Academic Integrity Violations (proctor teaching their own subject)
    - Section Daily Overloads (>3 exams or >2 majors in a day)
    - Proctor Daily Overloads (>8 hours in a day)
    """
    from datetime import datetime as _dt, timedelta as _td
    from collections import defaultdict
    import re
    
    close_when_done = False
    if db is None:
        db = open_db()
        close_when_done = True
        
    if not db:
        return {
            'is_clean': True,
            'total_exams': 0,
            'total_conflicts_count': 0,
            'conflict_exam_ids': [],
            'conflict_reasons': {},
            'room_conflicts': [],
            'proctor_conflicts': [],
            'section_conflicts': [],
            'subject_conflicts': [],
            'break_conflicts': [],
            'integrity_conflicts': [],
            'section_overloads': [],
            'proctor_overloads': []
        }
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.id, e.subject_name, e.section, e.subject_type, e.duration_minutes, e.exam_date_time,
                   e.room_id, r.room_name,
                   e.instructor_id, COALESCE(inst.name, e.instructor_name, 'TBA') as instructor_name,
                   inst.subjects_taught
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors inst ON e.instructor_id = inst.id
            WHERE e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL
            ORDER BY e.exam_date_time ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
    finally:
        if close_when_done:
            db.close()

    total_exams = len(rows)
    if total_exams == 0:
        return {
            'is_clean': True,
            'total_exams': 0,
            'total_conflicts_count': 0,
            'conflict_exam_ids': [],
            'conflict_reasons': {},
            'room_conflicts': [],
            'proctor_conflicts': [],
            'section_conflicts': [],
            'subject_conflicts': [],
            'break_conflicts': [],
            'integrity_conflicts': [],
            'section_overloads': [],
            'proctor_overloads': []
        }

    records = []
    for r in rows:
        st = r['exam_date_time']
        dur_mins = int(r.get('duration_minutes') or (120 if r.get('subject_type') == 'Major' else 60))
        end = st + _td(minutes=dur_mins)
        records.append({
            'id': r['id'],
            'subject': (r.get('subject_name') or 'Unknown').strip(),
            'section': (r.get('section') or '').strip(),
            'type': r.get('subject_type') or 'Major',
            'room_id': r.get('room_id'),
            'room_name': r.get('room_name') or f"Room {r.get('room_id')}",
            'instructor_id': r.get('instructor_id'),
            'instructor_name': r.get('instructor_name') or 'TBA',
            'subjects_taught': r.get('subjects_taught') or '',
            'start': st,
            'end': end,
            'dur_hours': dur_mins / 60.0,
            'date': st.date()
        })

    room_conflicts = []
    proctor_conflicts = []
    section_conflicts = []
    subject_conflicts = []
    break_conflicts = []
    integrity_conflicts = []
    conflict_exam_ids = set()
    conflict_reasons = defaultdict(list)

    # 1. Subject Desynchronization Check (sister sections taking same course at different times)
    subj_groups = defaultdict(list)
    for r in records:
        norm_subj = re.sub(r'\s+', '', r['subject'].upper())
        if norm_subj:
            subj_groups[norm_subj].append(r)

    for norm_subj, s_records in subj_groups.items():
        if len(s_records) > 1:
            times_map = defaultdict(list)
            for r in s_records:
                times_map[r['start']].append(r)
            if len(times_map) > 1:
                for r in s_records:
                    conflict_exam_ids.add(r['id'])
                    if 'subject' not in conflict_reasons[r['id']]:
                        conflict_reasons[r['id']].append('subject')
                s_name = s_records[0]['subject']
                details_list = [f"{r['section']} at {r['start'].strftime('%b %d %I:%M %p')}" for r in s_records]
                subject_conflicts.append({
                    'subject': s_name,
                    'count': len(s_records),
                    'details': ", ".join(details_list),
                    'reason': f"Subject '{s_name}' is split across {len(times_map)} different exam times ({', '.join(details_list)}). All sections of the same course must be held at the same time."
                })

    # 2. Academic Integrity Check: Proctor teaching their own course
    for r in records:
        if r['instructor_id'] and r['subjects_taught'] and r['subject']:
            subs = {s.strip().lower() for s in re.split(r'[,|;]', r['subjects_taught']) if s.strip()}
            s_low = r['subject'].lower()
            if s_low in subs or any(s_low == sub or sub in s_low for sub in subs):
                conflict_exam_ids.add(r['id'])
                if 'proctor' not in conflict_reasons[r['id']]:
                    conflict_reasons[r['id']].append('proctor')
                integrity_conflicts.append({
                    'exam_id': r['id'],
                    'proctor': r['instructor_name'],
                    'subject': r['subject'],
                    'section': r['section'],
                    'date': r['date'].strftime('%b %d, %Y'),
                    'time': f"{r['start'].strftime('%I:%M %p')} - {r['end'].strftime('%I:%M %p')}",
                    'reason': f"Instructor '{r['instructor_name']}' teaches '{r['subject']}' and is prohibited from proctoring this course."
                })

    # 3. Pairwise collisions: Room & Proctor double-bookings, Section clashes & break buffer
    for i in range(len(records)):
        r1 = records[i]
        for j in range(i + 1, len(records)):
            r2 = records[j]

            # Time interval overlap
            has_overlap = (r1['start'] < r2['end'] and r1['end'] > r2['start'])

            # Room collision (strictly concurrent)
            if has_overlap and r1['room_id'] and r2['room_id'] and r1['room_id'] == r2['room_id']:
                conflict_exam_ids.add(r1['id'])
                conflict_exam_ids.add(r2['id'])
                if 'room' not in conflict_reasons[r1['id']]: conflict_reasons[r1['id']].append('room')
                if 'room' not in conflict_reasons[r2['id']]: conflict_reasons[r2['id']].append('room')
                room_conflicts.append({
                    'room': r1['room_name'],
                    'date': r1['date'].strftime('%b %d, %Y'),
                    'time': f"{r1['start'].strftime('%I:%M %p')} - {r1['end'].strftime('%I:%M %p')}",
                    'exam1': f"{r1['subject']} ({r1['section']})",
                    'exam2': f"{r2['subject']} ({r2['section']})"
                })

            # Proctor collision (strictly concurrent)
            if has_overlap and r1['instructor_id'] and r2['instructor_id'] and r1['instructor_id'] == r2['instructor_id']:
                conflict_exam_ids.add(r1['id'])
                conflict_exam_ids.add(r2['id'])
                if 'proctor' not in conflict_reasons[r1['id']]: conflict_reasons[r1['id']].append('proctor')
                if 'proctor' not in conflict_reasons[r2['id']]: conflict_reasons[r2['id']].append('proctor')
                proctor_conflicts.append({
                    'proctor': r1['instructor_name'],
                    'date': r1['date'].strftime('%b %d, %Y'),
                    'time': f"{r1['start'].strftime('%I:%M %p')} - {r1['end'].strftime('%I:%M %p')}",
                    'room1': r1['room_name'],
                    'room2': r2['room_name'],
                    'exam1': f"{r1['subject']} ({r1['section']})",
                    'exam2': f"{r2['subject']} ({r2['section']})"
                })

            # Section collision (strictly concurrent or <1hr break)
            if r1['section'] and r2['section'] and r1['section'].lower() == r2['section'].lower():
                if has_overlap:
                    conflict_exam_ids.add(r1['id'])
                    conflict_exam_ids.add(r2['id'])
                    if 'section' not in conflict_reasons[r1['id']]: conflict_reasons[r1['id']].append('section')
                    if 'section' not in conflict_reasons[r2['id']]: conflict_reasons[r2['id']].append('section')
                    section_conflicts.append({
                        'section': r1['section'],
                        'date': r1['date'].strftime('%b %d, %Y'),
                        'time': f"{r1['start'].strftime('%I:%M %p')} - {r1['end'].strftime('%I:%M %p')}",
                        'exam1': r1['subject'],
                        'exam2': r2['subject']
                    })
                elif r1['date'] == r2['date']:
                    # Check break buffer between exams on same day
                    gap_mins = None
                    if r2['start'] >= r1['end']:
                        gap_mins = int((r2['start'] - r1['end']).total_seconds() / 60)
                    elif r1['start'] >= r2['end']:
                        gap_mins = int((r1['start'] - r2['end']).total_seconds() / 60)
                    if gap_mins is not None and gap_mins < 60:
                        conflict_exam_ids.add(r1['id'])
                        conflict_exam_ids.add(r2['id'])
                        if 'section' not in conflict_reasons[r1['id']]: conflict_reasons[r1['id']].append('section')
                        if 'section' not in conflict_reasons[r2['id']]: conflict_reasons[r2['id']].append('section')
                        break_conflicts.append({
                            'section': r1['section'],
                            'date': r1['date'].strftime('%b %d, %Y'),
                            'exam1': f"{r1['subject']} ({r1['start'].strftime('%I:%M %p')})",
                            'exam2': f"{r2['subject']} ({r2['start'].strftime('%I:%M %p')})",
                            'gap': gap_mins,
                            'reason': f"Section '{r1['section']}' has only {gap_mins} mins break between '{r1['subject']}' and '{r2['subject']}' (Minimum 1 hour break required)."
                        })

    # 4. Section daily limits (>3 exams or >2 majors in a day)
    sec_daily = defaultdict(lambda: defaultdict(list))
    for r in records:
        if r['section']:
            sec_daily[r['section']][r['date']].append(r)

    section_overloads = []
    for sec, days in sec_daily.items():
        for d, exs in days.items():
            tot = len(exs)
            maj = sum(1 for e in exs if e['type'] == 'Major')
            if tot > 3:
                for e in exs:
                    conflict_exam_ids.add(e['id'])
                    if 'daily_total' not in conflict_reasons[e['id']]: conflict_reasons[e['id']].append('daily_total')
                section_overloads.append({
                    'section': sec,
                    'date': d.strftime('%b %d, %Y'),
                    'reason': f"{tot} exams on this day (maximum 3 permitted)"
                })
            elif maj > 3:
                for e in exs:
                    conflict_exam_ids.add(e['id'])
                    if 'daily_major' not in conflict_reasons[e['id']]: conflict_reasons[e['id']].append('daily_major')
                section_overloads.append({
                    'section': sec,
                    'date': d.strftime('%b %d, %Y'),
                    'reason': f"{maj} major exams on this day (maximum 3 permitted with 1-hr break)"
                })
            elif maj == 3:
                # Permitted fallback only if minimum 1 hour break interval is respected between all exams
                sorted_exs = sorted(exs, key=lambda x: x['start'])
                has_break_violation = False
                for idx in range(len(sorted_exs) - 1):
                    gap_mins = (sorted_exs[idx+1]['start'] - sorted_exs[idx]['end']).total_seconds() / 60.0
                    if gap_mins < 60:
                        has_break_violation = True
                        break
                if has_break_violation:
                    for e in exs:
                        conflict_exam_ids.add(e['id'])
                        if 'daily_major' not in conflict_reasons[e['id']]: conflict_reasons[e['id']].append('daily_major')
                    section_overloads.append({
                        'section': sec,
                        'date': d.strftime('%b %d, %Y'),
                        'reason': f"3 major exams on this day require at least 1-hour break between each (insufficient break)"
                    })

    # 5. Proctor daily limits (>8.0 hours in a day)
    proctor_daily = defaultdict(lambda: defaultdict(float))
    for r in records:
        if r['instructor_id']:
            proctor_daily[(r['instructor_id'], r['instructor_name'])][r['date']] += r['dur_hours']

    proctor_overloads = []
    for (i_id, i_name), days in proctor_daily.items():
        for d, hrs in days.items():
            if hrs > 8.0:
                for r in records:
                    if r['instructor_id'] == i_id and r['date'] == d:
                        conflict_exam_ids.add(r['id'])
                        if 'daily_total' not in conflict_reasons[r['id']]: conflict_reasons[r['id']].append('daily_total')
                proctor_overloads.append({
                    'proctor': i_name,
                    'date': d.strftime('%b %d, %Y'),
                    'hours': round(hrs, 1),
                    'reason': f"{round(hrs, 1)} hours assigned today (maximum 8.0 hours permitted)"
                })

    tot_conflicts = (
        len(room_conflicts) +
        len(proctor_conflicts) +
        len(section_conflicts) +
        len(subject_conflicts) +
        len(break_conflicts) +
        len(integrity_conflicts) +
        len(section_overloads) +
        len(proctor_overloads)
    )

    return {
        'is_clean': tot_conflicts == 0,
        'total_exams': total_exams,
        'total_conflicts_count': tot_conflicts,
        'conflict_exam_ids': sorted(list(conflict_exam_ids)),
        'conflict_reasons': dict(conflict_reasons),
        'room_conflicts': room_conflicts,
        'proctor_conflicts': proctor_conflicts,
        'section_conflicts': section_conflicts,
        'subject_conflicts': subject_conflicts,
        'break_conflicts': break_conflicts,
        'integrity_conflicts': integrity_conflicts,
        'section_overloads': section_overloads,
        'proctor_overloads': proctor_overloads
    }
