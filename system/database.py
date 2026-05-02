import mysql.connector
from datetime import datetime, timedelta

def open_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="database222"
        )
    except mysql.connector.Error as err:
        print(f"Connection failed: {err}")
        return None

def register_user(full_name, email, password, role='student'):
    """
    Insert a new user. Returns:
      'ok'              — success
      'email_taken'     — that email is already registered
      'error'           — DB / unexpected error
    """
    db = open_db()
    if not db:
        return 'error'
    cursor = db.cursor()
    try:
        # Check duplicate email
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return 'email_taken'
        cursor.execute(
            "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)",
            (full_name, email, password, role)
        )
        db.commit()
        return 'ok'
    except Exception as e:
        print(f"Register error: {e}")
        return 'error'
    finally:
        db.close()


# ── DASHBOARD ──────────────────────────────────────────────────────────────────

def get_dashboard_stats():
    db = open_db()
    stats = {'total_exams': 0, 'rooms': 0, 'instructors': 0,
             'scheduled': 0, 'pending': 0}
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM exams")
            stats['total_exams'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM rooms")
            stats['rooms'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM instructors")
            stats['instructors'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM exams WHERE status = 'Scheduled'")
            stats['scheduled'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM exams WHERE status = 'Pending'")
            stats['pending'] = cursor.fetchone()[0]
        except Exception as e:
            print(f"Stats Error: {e}")
        finally:
            db.close()
    return stats

def get_upcoming_exams():
    db = open_db()
    exams = []
    if db:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT e.*, r.room_name, i.name AS instructor_full_name
            FROM exams e
            LEFT JOIN rooms r ON e.room_id = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            ORDER BY e.exam_date_time ASC, e.section ASC
        """
        cursor.execute(query)
        exams = cursor.fetchall()
        db.close()
    return exams

# ── ROOMS ──────────────────────────────────────────────────────────────────────

def get_all_rooms():
    db = open_db()
    rooms = []
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM rooms ORDER BY room_name ASC")
            rooms = cursor.fetchall()
        except Exception as e:
            print(f"Fetch Rooms Error: {e}")
        finally:
            db.close()
    return rooms

def add_room(room_name, capacity):
    db = open_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO rooms (room_name, capacity) VALUES (%s, %s)",
                           (room_name, capacity))
            db.commit()
        except Exception as e:
            print(f"Error adding room: {e}")
        finally:
            db.close()

def delete_room(room_id):
    """
    Delete a room. Returns None on success, or an error string if
    the room is still referenced by one or more exams.
    """
    db = open_db()
    if not db:
        return 'Database connection failed.'
    try:
        cursor = db.cursor(dictionary=True)
        # Check how many exams still reference this room
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM exams WHERE room_id = %s",
            (room_id,)
        )
        row = cursor.fetchone()
        if row and row['cnt'] > 0:
            n = row['cnt']
            return (
                f"Cannot delete this room — it is assigned to {n} "
                f"exam{'s' if n != 1 else ''}. "
                f"Reset the schedule or reassign those exams first."
            )
        cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
        db.commit()
        return None   # success
    except Exception as e:
        return f'Delete failed: {e}'
    finally:
        db.close()

# ── INSTRUCTORS ────────────────────────────────────────────────────────────────

def get_all_instructors():
    db = open_db()
    instructors = []
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            # Join with users to show the proctor's login email
            cursor.execute("""
                SELECT i.*, u.email AS proctor_email
                FROM instructors i
                LEFT JOIN users u
                  ON u.instructor_id = i.id AND u.role = 'proctor'
                ORDER BY i.name ASC
            """)
            instructors = cursor.fetchall()
        except Exception as e:
            print(f"Fetch Instructors Error: {e}")
        finally:
            db.close()
    return instructors

def add_instructor(name, department):
    """Add an instructor and automatically create a linked proctor login account."""
    db = open_db()
    if db:
        cursor = db.cursor()
        try:
            # 1. Insert the instructor record
            cursor.execute(
                "INSERT INTO instructors (name, department, status) VALUES (%s, %s, 'Active')",
                (name, department)
            )
            instructor_id = cursor.lastrowid

            # 2. Auto-generate proctor credentials
            email_name  = name.lower().replace(" ", ".")
            proctor_email    = f"{email_name}@cca.edu.ph"
            proctor_password = "proctor123"

            # 3. Check if that email is already taken; suffix with ID if so
            cursor.execute("SELECT id FROM users WHERE email = %s", (proctor_email,))
            if cursor.fetchone():
                proctor_email = f"{email_name}.{instructor_id}@cca.edu.ph"

            # 4. Create the proctor user account
            cursor.execute(
                "INSERT INTO users (full_name, email, password, role, instructor_id) "
                "VALUES (%s, %s, %s, 'proctor', %s)",
                (name, proctor_email, proctor_password, instructor_id)
            )

            db.commit()
            print(f"Instructor + proctor account created: {proctor_email}")
        except Exception as e:
            print(f"Error adding instructor: {e}")
        finally:
            db.close()

def delete_instructor(instructor_id):
    """
    Delete an instructor. Returns None on success, or an error string if
    the instructor is still assigned to one or more exams.
    """
    db = open_db()
    if not db:
        return 'Database connection failed.'
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM exams WHERE instructor_id = %s",
            (instructor_id,)
        )
        row = cursor.fetchone()
        if row and row['cnt'] > 0:
            n = row['cnt']
            return (
                f"Cannot delete this instructor — they are assigned to {n} "
                f"exam{'s' if n != 1 else ''}. "
                f"Reset the schedule or reassign those exams first."
            )
        cursor.execute("DELETE FROM instructors WHERE id = %s", (instructor_id,))
        db.commit()
        return None   # success
    except Exception as e:
        return f'Delete failed: {e}'
    finally:
        db.close()

# ── EXAMS ──────────────────────────────────────────────────────────────────────

def add_exam(name, section, subject_type, duration_minutes):
    """Add an exam without a fixed date/time — the scheduler assigns it later."""
    db = open_db()
    if db:
        cursor = db.cursor()
        try:
            duration_minutes = int(duration_minutes) if duration_minutes else 60
            section      = section.strip().upper() if section else None
            subject_type = subject_type if subject_type in ('Major', 'Minor') else 'Major'
            cursor.execute(
                """INSERT INTO exams
                   (subject_name, section, subject_type, duration_minutes, status)
                   VALUES (%s, %s, %s, %s, 'Pending')""",
                (name, section, subject_type, duration_minutes))
            db.commit()
        except Exception as e:
            print(f"Error adding exam: {e}")
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

def get_pending_exams():
    """Return exams that have not been scheduled yet (exam_date_time is NULL)."""
    db = open_db()
    exams = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, subject_name, section, subject_type, duration_minutes
               FROM exams
               WHERE exam_date_time IS NULL
                  OR status IN ('Pending', 'Unscheduled')"""
        )
        exams = cursor.fetchall()
        db.close()
    return exams

# ── SCHEDULER HELPERS ───────────────────────────────────────────────────

def get_already_scheduled_slots():
    """
    Returns already-Scheduled exams so the algorithm can respect
    existing bookings during a partial re-run.
    Includes subject_name so the same-subject-same-slot rule is upheld.
    """
    db = open_db()
    slots = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """SELECT room_id, instructor_id, exam_date_time,
                      duration_minutes, section, subject_type, subject_name
               FROM exams WHERE status = 'Scheduled'
                 AND exam_date_time IS NOT NULL"""
        )
        slots = cursor.fetchall()
        db.close()
    return slots


def apply_schedule_results(scheduled: list, failed_ids: list):
    """
    Write scheduler output to DB.
    scheduled  – list of {exam_id, room_id, instructor_id, instructor_name, exam_date_time}
    failed_ids – list of exam ids that could not be placed
    """
    db = open_db()
    if not db:
        return
    cursor = db.cursor()
    try:
        for item in scheduled:
            cursor.execute(
                """UPDATE exams
                   SET room_id = %s, instructor_id = %s,
                       instructor_name = %s, exam_date_time = %s,
                       status = 'Scheduled'
                   WHERE id = %s""",
                (item['room_id'], item['instructor_id'],
                 item['instructor_name'], item['exam_date_time'],
                 item['exam_id'])
            )
        for eid in failed_ids:
            cursor.execute(
                "UPDATE exams SET status = 'Unscheduled' WHERE id = %s", (eid,)
            )
        db.commit()
    except Exception as e:
        print(f"Error applying schedule: {e}")
        db.rollback()
    finally:
        db.close()

def reset_schedule():
    """Clear all scheduling assignments so the schedule can be re-generated."""
    db = open_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute(
                """UPDATE exams
                   SET room_id = NULL, instructor_id = NULL,
                       instructor_name = NULL, exam_date_time = NULL,
                       status = 'Pending'"""
            )
            db.commit()
        except Exception as e:
            print(f"Error resetting schedule: {e}")
        finally:
            db.close()

# ── PROCTOR AVAILABILITY ─────────────────────────────────────────────────

def save_proctor_availability(instructor_id: int, dates: list):
    """
    Replace the availability for a proctor.
    dates – list of date strings 'YYYY-MM-DD'
    """
    db = open_db()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM proctor_availability WHERE instructor_id = %s",
                       (instructor_id,))
        for d in dates:
            cursor.execute(
                "INSERT INTO proctor_availability (instructor_id, available_date) VALUES (%s, %s)",
                (instructor_id, d)
            )
        db.commit()
    except Exception as e:
        print(f"Error saving availability: {e}")
    finally:
        db.close()

def get_proctor_availability() -> dict:
    """
    Returns {instructor_id: set[date]} for all instructors.
    Empty set means no restrictions (available all days).
    """
    from datetime import date as _date
    db = open_db()
    result = {}
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT instructor_id, available_date FROM proctor_availability")
        for row in cursor.fetchall():
            iid = row['instructor_id']
            if iid not in result:
                result[iid] = set()
            d = row['available_date']
            result[iid].add(d if isinstance(d, _date) else _date.fromisoformat(str(d)))
        db.close()
    return result

def get_proctor_availability_for(instructor_id: int) -> list:
    """Return list of available date strings for one instructor."""
    db = open_db()
    dates = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT available_date FROM proctor_availability WHERE instructor_id = %s ORDER BY available_date",
            (instructor_id,)
        )
        dates = [str(r['available_date']) for r in cursor.fetchall()]
        db.close()
    return dates

# ── SCHEDULE VIEW ──────────────────────────────────────────────────────────────


def get_schedule_results():
    """
    Returns all exams joined with room and instructor info,
    ordered by date/time then section.
    """
    db = open_db()
    results = []
    if db:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT
                e.id,
                e.subject_name,
                e.section,
                e.subject_type,
                e.exam_date_time,
                e.duration_minutes,
                e.status,
                e.room_id,
                e.instructor_id,
                r.room_name,
                r.capacity,
                i.name  AS instructor_name,
                i.department
            FROM exams e
            LEFT JOIN rooms       r ON e.room_id       = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            ORDER BY e.exam_date_time ASC, e.section ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        db.close()
    return results


def get_exam_by_id(exam_id: int):
    """Return a single exam row with room + instructor details."""
    db = open_db()
    row = None
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, r.room_name, i.name AS instructor_name
            FROM exams e
            LEFT JOIN rooms       r ON e.room_id       = r.id
            LEFT JOIN instructors i ON e.instructor_id = i.id
            WHERE e.id = %s
        """, (exam_id,))
        row = cursor.fetchone()
        db.close()
    return row


def check_edit_conflicts(exam_id: int, new_room_id: int,
                         new_instructor_id: int, new_datetime_str: str,
                         duration_minutes: int):
    """
    Check whether the proposed edit would create any scheduling conflicts.

    Conflicts detected:
      1. Room double-booking   — same room overlaps another exam at the same time
      2. Instructor clash      — same instructor already proctoring another exam
      3. Same-subject drift    — another section of the SAME subject is scheduled
                                 at a DIFFERENT time (violates anti-cheat rule)

    Returns a list of conflict description strings (empty = no conflicts).
    """
    from datetime import datetime as _dt, timedelta as _td
    db = open_db()
    conflicts = []
    if not db:
        return ['Database connection failed.']
    try:
        cursor = db.cursor(dictionary=True)

        # Parse proposed start + end
        try:
            new_start = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_start = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')
        new_end = new_start + _td(minutes=duration_minutes)

        # ── 1. Room double-booking ────────────────────────────────────────
        cursor.execute("""
            SELECT subject_name, section, exam_date_time, duration_minutes
            FROM exams
            WHERE room_id = %s
              AND id != %s
              AND status = 'Scheduled'
              AND exam_date_time IS NOT NULL
        """, (new_room_id, exam_id))
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str):
                r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                conflicts.append(
                    f"⚠️ Room conflict: room is already used by "
                    f"\"{row['subject_name']}\" "
                    f"({row['section'] or '—'}) "
                    f"at {r_start.strftime('%b %d, %I:%M %p')}."
                )

        # ── 2. Instructor double-booking ──────────────────────────────────
        cursor.execute("""
            SELECT subject_name, section, exam_date_time, duration_minutes
            FROM exams
            WHERE instructor_id = %s
              AND id != %s
              AND status = 'Scheduled'
              AND exam_date_time IS NOT NULL
        """, (new_instructor_id, exam_id))
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str):
                r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                conflicts.append(
                    f"⚠️ Instructor conflict: proctor is already assigned to "
                    f"\"{row['subject_name']}\" "
                    f"({row['section'] or '—'}) "
                    f"at {r_start.strftime('%b %d, %I:%M %p')}."
                )

        # ── 3. Same-subject at different time (anti-cheat) ────────────────
        cursor.execute("""
            SELECT section, exam_date_time
            FROM exams
            WHERE subject_name = (SELECT subject_name FROM exams WHERE id = %s)
              AND id != %s
              AND status = 'Scheduled'
              AND exam_date_time IS NOT NULL
        """, (exam_id, exam_id))
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str):
                r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            if r_start != new_start:
                conflicts.append(
                    f"🚫 Anti-cheat violation: section \"{row['section'] or '—'}\" "
                    f"sits the same subject at {r_start.strftime('%b %d, %I:%M %p')}. "
                    f"All sections must take the same subject at the same time."
                )

    except Exception as e:
        conflicts.append(f'Conflict check error: {e}')
    finally:
        db.close()
    return conflicts


def apply_exam_edit(exam_id: int, new_room_id: int,
                    new_instructor_id: int, new_datetime_str: str):
    """Persist a manually edited exam slot."""
    from datetime import datetime as _dt
    db = open_db()
    if not db:
        return False
    try:
        cursor = db.cursor()
        try:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE exams
            SET room_id = %s, instructor_id = %s, exam_date_time = %s
            WHERE id = %s
        """, (new_room_id, new_instructor_id, new_dt, exam_id))
        db.commit()
        return True
    except Exception as e:
        print(f'apply_exam_edit error: {e}')
        return False
    finally:
        db.close()



def check_conflict(date_time, room_id, instructor_name):
    """Legacy point-in-time conflict check — superseded by the scheduler module."""
    db = open_db()
    has_conflict = False
    if db:
        cursor = db.cursor()
        query = """
            SELECT COUNT(*) FROM exams
            WHERE exam_date_time = %s
            AND (room_id = %s OR instructor_name = %s)
            AND status = 'Scheduled'
        """
        cursor.execute(query, (date_time, room_id, instructor_name))
        result = cursor.fetchone()
        if result and result[0] > 0:
            has_conflict = True
        db.close()
    return has_conflict

def update_exam_schedule(exam_id, room_id, instructor_name):
    """Legacy updater — superseded by apply_schedule_results()."""
    db = open_db()
    if db:
        cursor = db.cursor()
        cursor.execute(
            """UPDATE exams
               SET room_id = %s, instructor_name = %s, status = 'Scheduled'
               WHERE id = %s""",
            (room_id, instructor_name, exam_id))
        db.commit()
        db.close()

# ── PROCTOR MODULE ─────────────────────────────────────────────────────────────

def get_proctor_exams(instructor_id: int):
    """
    Return all exams assigned to a specific instructor (proctor).
    Ordered by exam date/time then section.
    """
    db = open_db()
    exams = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """SELECT
                   e.id,
                   e.subject_name,
                   e.section,
                   e.exam_date_time,
                   e.duration_minutes,
                   e.status,
                   r.room_name,
                   r.capacity
               FROM exams e
               LEFT JOIN rooms r ON e.room_id = r.id
               WHERE e.instructor_id = %s
               ORDER BY e.exam_date_time ASC, e.section ASC""",
            (instructor_id,)
        )
        exams = cursor.fetchall()
        db.close()
    return exams

# ── STUDENT MODULE ─────────────────────────────────────────────────────────────

def get_public_timetable():
    """
    Return all Scheduled exams for the public student timetable view.
    Only exposes non-sensitive fields (no internal IDs).
    """
    db = open_db()
    exams = []
    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """SELECT
                   e.subject_name,
                   e.section,
                   e.subject_type,
                   e.exam_date_time,
                   e.duration_minutes,
                   r.room_name,
                   i.name  AS proctor_name,
                   i.department
               FROM exams e
               LEFT JOIN rooms       r ON e.room_id       = r.id
               LEFT JOIN instructors i ON e.instructor_id = i.id
               WHERE e.status = 'Scheduled'
               ORDER BY e.exam_date_time ASC, e.section ASC"""
        )
        exams = cursor.fetchall()
        db.close()
    return exams