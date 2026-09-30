"""
app.py — CCA Exam Management System v2
Full 50-feature implementation.
Run:  python app.py
"""
from flask import (Flask, render_template, session, redirect, url_for,
                   request, flash, jsonify, send_file, make_response)
from flask_mail import Mail, Message as MailMessage
from datetime import date, datetime, timedelta
from collections import defaultdict
import io, os

import secrets
from datetime import datetime, timedelta
from system.mailer import send_reset_email
from system.database import (
    set_password_reset_token, get_user_by_reset_token, get_user_by_email, clear_reset_token_and_update_password,
    # settings
    get_system_settings, save_system_settings,
    # institutes
    get_all_institutes, add_institute, edit_institute, delete_institute,
    # subjects
    get_all_subjects, get_subjects_by_institute, add_subject, edit_subject,
    delete_subject, link_subjects_content_group, unlink_subject_content_group,
    get_common_subjects,
    get_subject_content_groups, bulk_import_subjects,
    # users
    register_user, get_all_users, get_user_by_id, update_user, delete_user,
    get_all_students, get_pending_users, approve_student,
    deactivate_student, bulk_deactivate_students, bulk_delete_students,
    # rooms
    get_all_rooms, get_rooms_by_institute, add_room, edit_room, delete_room,
    bulk_import_rooms,
    # instructors / faculty
    get_all_instructors, get_active_instructors, get_instructor_by_id,
    add_instructor, edit_instructor, deactivate_instructor, activate_instructor,
    delete_instructor, bulk_import_instructors,
    get_proctor_total_hours, get_all_proctor_hours_summary,
    # exams
    get_dashboard_stats, get_upcoming_exams, add_exam, edit_exam_details,
    delete_exam, delete_all_exams, get_pending_exams, get_all_exams, get_exam_by_id,
    get_student_exam_load_per_day, bulk_import_exams, bulk_delete_exams,
    # scheduling
    get_already_scheduled_slots, apply_schedule_results, reset_schedule, unschedule_exams,
    get_schedule_results, check_edit_conflicts, apply_exam_edit, get_available_resources,
    save_exam_period, save_exam_term, get_exam_term, get_exam_period, save_exam_term, get_exam_term,
    # proctor availability
    get_proctor_availability, get_proctor_availability_for, save_proctor_availability,
    get_proctor_exams,
    # timetable
    get_public_timetable,
    # relievers
    add_reliever, get_relievers_for_exam, get_all_relievers, remove_reliever,
    # secretary
    get_exam_collection_status, mark_exam_collected, mark_exam_returned,
    get_collection_stats,
    # absence
    record_proctor_absence, get_proctor_absence_report, get_absence_stats,
    # notifications
    create_notification, get_notifications, get_unread_count,
    mark_notification_read, mark_all_read, create_notification_for_role,
    # reports
    get_scheduling_report, get_assignment_report, get_student_exam_load_report,
    # period
    open_db,
)
from system.scheduler import run_scheduler
from system.logic import verify_login, is_super_admin, hash_password

# ── FLASK APP ─────────────────────────────────────────────────────────────────


import firebase_admin
from firebase_admin import credentials, auth as fb_auth

try:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)
except ValueError:
    pass # Already initialized

app = Flask(__name__, template_folder='template')
app.secret_key = "cca_exam_management_secret_key_v2"

# ── MAIL ──────────────────────────────────────────────────────────────────────

def _configure_mail():
    try:
        s = get_system_settings()
    except Exception:
        s = {}
    app.config['MAIL_SERVER']         = s.get('smtp_host', '') or ''
    app.config['MAIL_PORT']           = int(s.get('smtp_port') or 587)
    app.config['MAIL_USERNAME']       = s.get('smtp_user', '') or ''
    app.config['MAIL_PASSWORD']       = s.get('smtp_password', '') or ''
    app.config['MAIL_DEFAULT_SENDER'] = s.get('smtp_from', '') or ''
    app.config['MAIL_USE_TLS']        = bool(s.get('smtp_use_tls', 1))
    app.config['MAIL_USE_SSL']        = False
    app.config['MAIL_TIMEOUT']        = 5
    app.config['MAIL_SUPPRESS_SEND']  = not bool(app.config['MAIL_SERVER'])
    
    # Re-initialize the Mail extension to pick up these new config values immediately
    if hasattr(app, 'extensions') and 'mail' in app.extensions:
        mail.init_app(app)

_configure_mail()
mail = Mail(app)

def send_email_notification(to_email, subject, body):
    """Send an email in a background thread. Silently skips if SMTP not configured."""
    if not app.config.get('MAIL_SERVER'):
        return
    import threading
    def _send():
        try:
            with app.app_context():
                msg = MailMessage(subject=subject, recipients=[to_email], body=body)
                mail.send(msg)
        except Exception as e:
            print(f"[Mail Error] {e}")
    threading.Thread(target=_send, daemon=True).start()

# ── HELPERS ───────────────────────────────────────────────────────────────────

def require_login():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return None

def require_role(*roles):
    redir = require_login()
    if redir:
        return redir
    if session.get('role') not in roles:
        return _redirect_by_role()
    return None

def _redirect_by_role():
    role = session.get('role')
    if role in ('admin',):
        return redirect(url_for('dashboard'))
    elif role == 'proctor':
        return redirect(url_for('proctor_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_timetable'))
    elif role == 'secretary':
        return redirect(url_for('secretary_dashboard'))
    session.clear()
    return redirect(url_for('login'))

def _get_unread(user_id):
    try:
        return get_unread_count(user_id)
    except Exception:
        return 0

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if 'user_id' in session:
        if not session.get('role'):
            session.clear()
        else:
            return _redirect_by_role()
    return redirect(url_for('login'))

@app.route("/public/timetable")
def public_timetable():
    section = request.args.get('section', '').strip()
    if not section:
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("irregular_portal.html", sections=sections)
    
    exams = get_public_timetable(section=section)
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt: continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        exam['time']     = dt.strftime("%I:%M %p")
        exam['time_end'] = (dt + timedelta(minutes=int(exam['duration_minutes'] or 60))).strftime("%I:%M %p")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    
    sorted_groups = sorted(grouped.items(), key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name="Irregular Student Viewer",
                           institute_name="City College of Angeles",
                           exam_term=get_exam_term()[0],
                           exam_semester=get_exam_term()[1])


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = get_user_by_email(email)
        if user:
            token = secrets.token_urlsafe(32)
            expiry = datetime.now() + timedelta(hours=1)
            set_password_reset_token(email, token, expiry)
            
            reset_link = url_for('reset_password', token=token, _external=True)
            success, msg = send_reset_email(email, reset_link)
            
            if success:
                flash("Password reset link sent to your email.", "success")
            else:
                flash(f"Error sending email. (Check terminal for test link). Error: {msg}", "warning")
        else:
            # For security, don't reveal if email exists, just say we sent it
            flash("If that email is registered, a reset link was sent.", "info")
            
        return redirect(url_for("login"))
    return render_template("forgot_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = get_user_by_reset_token(token)
    
    if not user:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("login"))
        
    # Check expiry
    if user['reset_token_expiry'] and user['reset_token_expiry'] < datetime.now():
        flash("Reset link has expired. Please request a new one.", "error")
        return redirect(url_for("forgot_password"))
        
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        
        if not new_password or len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("reset_password.html", token=token)
            
        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html", token=token)
            
        from system.logic import hash_password
        hashed = hash_password(new_password)
        clear_reset_token_and_update_password(token, hashed)
        
        flash("Password successfully reset! You can now log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("reset_password.html", token=token)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session and session.get('role'):
            return _redirect_by_role()
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("login.html", sections=sections)

    
    firebase_token = request.form.get("firebase_token")
    if not firebase_token:
        flash("Firebase authentication failed. Missing token.", "error")
        return redirect(url_for('login'))
        
    try:
        decoded_token = fb_auth.verify_id_token(firebase_token)
        email = decoded_token.get('email')
        
        user = get_user_by_email(email)
        if not user:
            flash("User not found in system.", "error")
            return redirect(url_for('login'))
            
        session['user_id']        = user['id']
        session['full_name']      = user['full_name']
        session['role']           = user.get('role', 'student')
        session['email']          = user['email']
        session['section']        = user.get('section', '')
        session['institute_id']   = user.get('institute_id')
        session['instructor_id']  = user.get('instructor_id')
        session['is_super_admin'] = bool(user.get('is_super_admin', 0))
        
        return _redirect_by_role()
    except Exception as e:
        flash(f"Invalid login session: {str(e)}", "error")
        return redirect(url_for('login'))

        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("login.html", sections=sections)

    # POST - process credentials
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    user = verify_login(email, password)
    if user == 'inactive':
        flash("Your account is pending admin approval. You will be notified once it is activated.", "warning")
        return redirect(url_for('login'))
    if user:
        session.clear()
        session['user_id']        = user['id']
        session['full_name']      = user['full_name']
        session['role']           = user.get('role', 'student')
        session['instructor_id']  = user.get('instructor_id')
        session['is_super_admin'] = bool(user.get('is_super_admin', 0))
        session['section']        = user.get('section', '')
        session['institute_id']   = user.get('institute_id')
        return _redirect_by_role()
    flash("Invalid email or password.", "error")
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── REGISTER ──────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET"])
def register_page():
    if 'user_id' in session:
        return _redirect_by_role()
    institutes = get_all_institutes()
    
    # Get distinct sections
    sections = []
    from system.database import open_db
    db = open_db()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT section FROM (SELECT section FROM users WHERE section IS NOT NULL AND section != '' UNION SELECT section FROM exams WHERE section IS NOT NULL AND section != '') AS all_sections ORDER BY section")
            sections = [r[0] for r in cursor.fetchall()]
        finally:
            db.close()
            
    return render_template("register.html", institutes=institutes, sections=sections)

@app.route("/register", methods=["POST"])
def register_submit():
    first_name   = request.form.get("first_name", "").strip()
    last_name    = request.form.get("last_name", "").strip()
    middle_name  = request.form.get("middle_name", "").strip()
    suffix       = request.form.get("suffix", "").strip()
    
    # Format the name: "Lastname, Firstname M. Suffix"
    middle_initial = (middle_name[0].upper() + ".") if middle_name else ""
    full_name_parts = [part for part in [first_name, middle_initial, suffix] if part]
    formatted_first_part = " ".join(full_name_parts)
    full_name = f"{last_name}, {formatted_first_part}" if last_name and formatted_first_part else (last_name or formatted_first_part)
    email        = request.form.get("email", "").strip()
    password     = request.form.get("password", "").strip()
    section      = request.form.get("section", "").strip()
    institute_id = request.form.get("institute_id") or None
    role         = request.form.get("role", "student").strip()
    
    if role not in ['student', 'proctor']:
        role = 'student'
        
    if not email.endswith("@cca.edu.ph"):
        flash("Registration is restricted to @cca.edu.ph email addresses only.", "danger")
        return redirect(url_for('register_page'))
        
    import re as regex
    if len(password) < 8 or not regex.search(r'[A-Z]', password) or not regex.search(r'\d', password):
        flash("Password must be at least 8 characters long and contain at least one uppercase letter and one number.", "danger")
        return redirect(url_for('register_page'))

    if not full_name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('register_page'))
        
    # Check if user already exists in MySQL
    user_exists = get_user_by_email(email)
    if user_exists:
        flash("That email is already registered.", "danger")
        return redirect(url_for('register_page'))
        
    # Try creating user in Firebase FIRST so we catch Firebase duplicates
    try:
        from firebase_admin import auth as fb_auth
        fb_auth.create_user(email=email, password=password, display_name=full_name)
    except fb_auth.EmailAlreadyExistsError:
        # User is in Firebase but not in MySQL (orphaned due to past rejection).
        # Safe to delete and recreate.
        try:
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.delete_user(fb_user.uid)
            fb_auth.create_user(email=email, password=password, display_name=full_name)
        except Exception as e:
            flash("That email is already registered in the cloud auth system.", "danger")
            return redirect(url_for('register_page'))
    except Exception as e:
        flash(f"Cloud Auth Error: {str(e)}", "danger")
        return redirect(url_for('register_page'))

    # Create user in local MySQL
    result = register_user(full_name, email, password, role, section=section, institute_id=institute_id)
                           
    if result == 'ok':
        flash("Account created! Your registration is pending admin approval. You will be notified once it is activated.", "success")
        return redirect(url_for('login'))
    else:
        flash("Something went wrong saving to the local database.", "danger")
        return redirect(url_for('register_page'))

# --- ADMIN DASHBOARD ---

@app.route("/dashboard")
def dashboard():
    guard = require_role('admin')
    if guard: return guard
    stats           = get_dashboard_stats()
    exams           = get_all_exams()
    rooms           = get_all_rooms()
    instructors     = get_all_instructors()
    institutes      = get_all_institutes()
    subjects        = get_all_subjects()
    upcoming_exams  = get_upcoming_exams()
    settings        = get_system_settings()
    unread          = _get_unread(session['user_id'])
    pending_count   = len(get_pending_users())
    return render_template("dashboard.html",
                           stats=stats, exams=exams,
                           rooms=rooms, instructors=instructors,
                           institutes=institutes, subjects=subjects,
                           upcoming_exams=upcoming_exams,
                           settings=settings,
                           unread_count=unread,
                           pending_count=pending_count)

# ── ADD ROUTES ────────────────────────────────────────────────────────────────

@app.route("/add_room", methods=["POST"])
def create_room():
    guard = require_role('admin')
    if guard: return guard
    room_name = request.form.get("room_name", "").strip()
    building = request.form.get("building", "").strip()
    
    existing_rooms = get_all_rooms()
    if any(r['room_name'].lower() == room_name.lower() and r.get('building', '').lower() == building.lower() for r in existing_rooms):
        flash(f"Warning: Room '{room_name}' already exists in that building.", "error")
        return redirect(url_for('dashboard') + '#rooms')

    add_room(
        room_name,
        request.form.get("capacity"),
        building=request.form.get("building", ""),
        floor=request.form.get("floor", 1),
        institute_id=request.form.get("institute_id") or None,
        is_pwd_accessible=1 if request.form.get("is_pwd_accessible") else 0
    )
    flash("Room added successfully.", "success")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/add_instructor", methods=["POST"])
def create_instructor():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    
    existing_instructors = get_all_instructors()
    if any(i['name'].lower() == name.lower() for i in existing_instructors):
        flash(f"Warning: Instructor '{name}' is already registered in the system.", "error")
        return redirect(url_for('dashboard') + '#instructors')

    add_instructor(
        name,
        institute_id=request.form.get("institute_id") or None,
        building=request.form.get("building", ""),
        is_pwd=1 if request.form.get("is_pwd") else 0,
        subjects_taught=request.form.get("subjects_taught", "")
    )
    flash("Instructor added and proctor account created.", "success")
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/add_exam", methods=["POST"])
def create_exam():
    guard = require_role('admin')
    if guard: return guard
    subject_id = request.form.get("subject_id")
    section = request.form.get("section", "").strip()
    
    existing_exams = get_all_exams()
    if any(str(e.get('subject_id')) == str(subject_id) and e.get('section', '').lower() == section.lower() for e in existing_exams):
        flash(f"Warning: An exam for this subject and section already exists.", "error")
        return redirect(url_for('dashboard') + '#exams')

    # Auto-fetch subject name to ensure it exactly matches the linked subject
    existing_subjects = get_all_subjects()
    subject_name = next((s['name'] for s in existing_subjects if str(s['id']) == str(subject_id)), request.form.get("name", "Unknown"))

    add_exam(
        subject_name,
        request.form.get("section", "").strip(),
        request.form.get("subject_type", "Major"),
        int(float(request.form.get("duration_hours", 1)) * 60),
        institute_id=request.form.get("institute_id") or None,
        subject_id=request.form.get("subject_id") or None
    )
    flash("Exam added.", "success")
    return redirect(url_for('dashboard') + '#exams')

# ── EDIT ROUTES ───────────────────────────────────────────────────────────────

@app.route("/edit_room/<int:id>", methods=["POST"])
def update_room(id):
    guard = require_role('admin')
    if guard: return guard
    edit_room(
        id,
        request.form.get("room_name"),
        request.form.get("capacity"),
        request.form.get("building", ""),
        request.form.get("floor", 1),
        request.form.get("institute_id") or None,
        1 if request.form.get("is_pwd_accessible") else 0
    )
    flash("Room updated.", "success")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/edit_instructor/<int:id>", methods=["POST"])
def update_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    edit_instructor(
        id,
        request.form.get("name"),
        request.form.get("institute_id") or None,
        request.form.get("building", ""),
        1 if request.form.get("is_pwd") else 0,
        request.form.get("subjects_taught", "")
    )
    flash("Instructor updated.", "success")
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/edit_exam_details/<int:id>", methods=["POST"])
def update_exam_details(id):
    guard = require_role('admin')
    if guard: return guard
    edit_exam_details(
        id,
        request.form.get("name"),
        request.form.get("section", "").strip(),
        request.form.get("subject_type", "Major"),
        int(float(request.form.get("duration_hours", 1)) * 60),
        request.form.get("institute_id") or None,
        request.form.get("subject_id") or None
    )
    flash("Exam updated.", "success")
    return redirect(url_for('dashboard') + '#exams')

# ── DEACTIVATE / ACTIVATE ─────────────────────────────────────────────────────

@app.route("/deactivate_instructor/<int:id>", methods=["POST"])
def deact_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    deactivate_instructor(id)
    flash("Instructor deactivated.", "warning")
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/activate_instructor/<int:id>", methods=["POST"])
def act_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    activate_instructor(id)
    flash("Instructor activated.", "success")
    return redirect(url_for('dashboard') + '#instructors')

# ── DELETE ROUTES ─────────────────────────────────────────────────────────────

@app.route("/delete_room/<int:id>")
def remove_room(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_room(id)
    if err:
        flash(f'Cannot delete room: {err}', 'danger')
    else:
        flash('Room deleted.', 'success')
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/rooms/bulk_delete", methods=["POST"])
def bulk_delete_rooms():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist('room_ids')
    if not ids:
        flash("No rooms selected.", "warning")
        return redirect(url_for('dashboard') + '#rooms')
    deleted, errors = 0, []
    for sid in ids:
        try:
            err = delete_room(int(sid))
            if err:
                errors.append(err)
            else:
                deleted += 1
        except Exception as e:
            errors.append(str(e))
    if deleted:
        flash(f"✅ {deleted} room(s) deleted successfully.", "success")
    if errors:
        flash(f"⚠️ {len(errors)} room(s) could not be deleted: " + "; ".join(errors), "warning")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/delete_instructor/<int:id>")
def remove_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_instructor(id)
    if err:
        flash(f'Cannot delete instructor: {err}', 'danger')
    else:
        flash('Instructor deleted.', 'success')
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/instructors/bulk_delete", methods=["POST"])
def bulk_delete_instructors():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist('instructor_ids')
    if not ids:
        flash("No instructors selected.", "warning")
        return redirect(url_for('dashboard') + '#instructors')
    deleted, errors = 0, []
    for sid in ids:
        try:
            err = delete_instructor(int(sid))
            if err:
                errors.append(err)
            else:
                deleted += 1
        except Exception as e:
            errors.append(str(e))
    if deleted:
        flash(f"✅ {deleted} instructor(s) deleted successfully.", "success")
    if errors:
        flash(f"⚠️ {len(errors)} instructor(s) could not be deleted: " + "; ".join(errors), "warning")
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/faculty/bulk_delete", methods=["POST"])
def bulk_delete_faculty():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist('instructor_ids')
    if not ids:
        flash("No instructors selected.", "warning")
        return redirect(url_for('faculty_page'))
    deleted, errors = 0, []
    for sid in ids:
        try:
            err = delete_instructor(int(sid))
            if err:
                errors.append(err)
            else:
                deleted += 1
        except Exception as e:
            errors.append(str(e))
    if deleted:
        flash(f"✅ {deleted} instructor(s) deleted successfully.", "success")
    if errors:
        flash(f"⚠️ {len(errors)} instructor(s) could not be deleted: " + "; ".join(errors), "warning")
    return redirect(url_for('faculty_page'))

@app.route("/delete_exam/<int:id>")
def remove_exam(id):
    guard = require_role('admin')
    if guard: return guard
    delete_exam(id)
    flash('Exam deleted.', 'success')
    return redirect(url_for('dashboard') + '#exams')

@app.route("/delete_all_exams", methods=["POST"])
def remove_all_exams():
    guard = require_role('admin')
    if guard: return guard
    count = delete_all_exams()
    flash(f'✅ All {count} exam(s) deleted successfully.', 'success')
    return redirect(url_for('dashboard') + '#exams')

# ── SCHEDULE ──────────────────────────────────────────────────────────────────

@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    guard = require_role('admin')
    if guard: return guard

    period_start_str = request.form.get("period_start")
    period_end_str   = request.form.get("period_end")
    exam_term = request.form.get("exam_term", "Midterm")
    exam_semester = request.form.get("exam_semester", "1st Semester")
    save_exam_term(exam_term, exam_semester)
    try:
        period_start = date.fromisoformat(period_start_str)
        period_end   = date.fromisoformat(period_end_str)
    except (TypeError, ValueError):
        flash("Please select a valid exam period.", "warning")
        return redirect(url_for('schedule_view'))

    if period_end < period_start:
        flash("End date must be after start date.", "warning")
        return redirect(url_for('schedule_view'))

    save_exam_period(period_start, period_end)

    pending     = get_pending_exams()
    rooms       = get_all_rooms()
    instructors = get_active_instructors()
    booked      = get_already_scheduled_slots()
    proctor_av  = get_proctor_availability()
    settings    = get_system_settings()

    if not rooms:
        flash("⚠️ No rooms found. Add at least one room first.", "warning")
        return redirect(url_for('schedule_view'))
    if not instructors:
        flash("⚠️ No active instructors found.", "warning")
        return redirect(url_for('schedule_view'))
    if not pending:
        flash("ℹ️ No pending exams to schedule.", "info")
        return redirect(url_for('schedule_view'))

    result = run_scheduler(
        pending_exams=pending,
        rooms=rooms,
        instructors=instructors,
        booked_slots=booked,
        period_start=period_start,
        period_end=period_end,
        proctor_availability=proctor_av,
        settings=settings
    )

    failed_ids = [f['exam_id'] for f in result['failed']]
    apply_schedule_results(result['scheduled'], failed_ids)
    session['last_failed']          = result['failed']
    session['last_scheduled_count'] = len(result['scheduled'])

    # Email notifications to assigned proctors
    db = open_db()
    if db:
        try:
            c = db.cursor(dictionary=True)
            for item in result['scheduled']:
                c.execute("""
                    SELECT u.email, u.full_name, e.subject_name, e.section, e.exam_date_time
                    FROM exams e
                    JOIN users u ON u.instructor_id = e.instructor_id
                    WHERE e.id = %s
                """, (item['exam_id'],))
                row = c.fetchone()
                if row and row.get('email'):
                    dt = row['exam_date_time']
                    dt_str = dt.strftime('%B %d, %Y at %I:%M %p') if dt else 'TBD'
                    send_email_notification(
                        row['email'],
                        f"CCA Exam Proctoring Assignment — {row['subject_name']}",
                        f"Dear {row['full_name']},\n\nYou have been assigned to proctor:\n"
                        f"Subject: {row['subject_name']} ({row['section'] or '—'})\n"
                        f"Date/Time: {dt_str}\n\nPlease log in to view full details.\n\n"
                        f"CCA Exam Management System"
                    )
        except Exception as e:
            print(f"[Email batch error] {e}")
        finally:
            db.close()

    flash(f"✅ Scheduled {len(result['scheduled'])} exam(s). "
          f"{len(result['failed'])} could not be placed.", "success")
    return redirect(url_for('schedule_view'))

@app.route("/reset_schedule", methods=["GET", "POST"])
def reset_schedule_route():
    guard = require_role('admin')
    if guard: return guard
    reset_schedule()
    session.pop('last_failed', None)
    session.pop('last_scheduled_count', None)
    flash('Schedule reset. All exams are back to Pending.', 'success')
    return redirect(url_for('schedule_view'))

@app.route("/resolve_conflicts", methods=["POST"])
def resolve_conflicts_route():
    guard = require_role('admin')
    if guard: return guard
    
    conflict_ids_str = request.form.get("conflict_ids", "")
    if not conflict_ids_str:
        flash("No conflicts to resolve.", "info")
        return redirect(url_for('schedule_view'))
        
    try:
        exam_ids = [int(x.strip()) for x in conflict_ids_str.split(",") if x.strip()]
    except ValueError:
        flash("Invalid conflict IDs.", "danger")
        return redirect(url_for('schedule_view'))
        
    if not exam_ids:
        return redirect(url_for('schedule_view'))
        
    # Unschedule the conflicting exams
    unschedule_exams(exam_ids)
    
    # Run the scheduler again, which will now try to place these newly unscheduled exams
    # while keeping all other scheduled exams locked
    period_start, period_end = get_exam_period()
    if not period_start or not period_end:
        flash("Exam period not set.", "warning")
        return redirect(url_for('schedule_view'))
        
    pending = get_pending_exams()
    rooms = get_all_rooms()
    instructors = get_active_instructors()
    booked = get_already_scheduled_slots()
    proctor_av = get_proctor_availability()
    settings = get_system_settings()
    
    result = run_scheduler(
        pending_exams=pending,
        rooms=rooms,
        instructors=instructors,
        booked_slots=booked,
        period_start=period_start,
        period_end=period_end,
        proctor_availability=proctor_av,
        settings=settings
    )
    
    failed_ids = [f['exam_id'] for f in result['failed']]
    apply_schedule_results(result['scheduled'], failed_ids)
    
    session['last_failed'] = result['failed']
    session['last_scheduled_count'] = len(result['scheduled'])
    
    if failed_ids:
        flash(f"Auto-resolve completed, but {len(failed_ids)} exam(s) could still not be scheduled.", "warning")
    else:
        flash("✅ All conflicts have been successfully auto-resolved!", "success")
        
    return redirect(url_for('schedule_view'))

@app.route("/schedule")
def schedule_view():
    guard = require_role('admin')
    if guard: return guard
    all_exams   = get_schedule_results()
    failed      = session.pop('last_failed', [])
    
    # Enrich each exam with parsed datetime, formatted strings
    scheduled_exams = []
    unscheduled     = []
    for exam in all_exams:
        if exam['status'] == 'Scheduled':
            dt = exam['exam_date_time']
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            exam['_dt']       = dt
            exam['_date_str'] = dt.strftime("%Y-%m-%d")          # for grouping
            exam['_time_str'] = dt.strftime("%H:%M")             # row key
            exam['_date_label'] = dt.strftime("%a %b %d")       # column header
            exam['datetime']  = dt.strftime("%b %d, %Y %I:%M %p")
            exam['datetime_raw'] = dt.strftime("%Y-%m-%dT%H:%M")
            scheduled_exams.append(exam)
        else:
            unscheduled.append(exam)

    # Detect conflicts
    conflict_ids = set()
    conflict_reasons = {}   # exam_id -> set of reason strings
    def _add_conflict(eid, reason):
        conflict_ids.add(eid)
        conflict_reasons.setdefault(eid, set()).add(reason)

    for i, a in enumerate(scheduled_exams):
        end_a = a['_dt'] + timedelta(minutes=a['duration_minutes'] or 60)
        for b in scheduled_exams[i+1:]:
            end_b = b['_dt'] + timedelta(minutes=b['duration_minutes'] or 60)
            overlaps = a['_dt'] < end_b and b['_dt'] < end_a
            # Room conflict: same room, overlapping time
            if overlaps and a.get('room_id') and a['room_id'] == b.get('room_id'):
                _add_conflict(a['id'], 'room'); _add_conflict(b['id'], 'room')
            # Proctor conflict: same instructor/proctor, overlapping time
            if overlaps and a.get('instructor_id') and a['instructor_id'] == b.get('instructor_id'):
                _add_conflict(a['id'], 'proctor'); _add_conflict(b['id'], 'proctor')
            # Section conflict: same section sitting two different exams at the same time OR less than 1 hour break
            sec_a = (a.get('section') or '').strip()
            sec_b = (b.get('section') or '').strip()
            if sec_a and sec_a == sec_b:
                a_buf_start = a['_dt'] - timedelta(hours=1)
                a_buf_end = end_a + timedelta(hours=1)
                if a_buf_start < end_b and b['_dt'] < a_buf_end:
                    _add_conflict(a['id'], 'section'); _add_conflict(b['id'], 'section')
            # Subject conflict: same subject scheduled at different times
            subj_a = (a.get('subject_name') or '').strip().lower()
            subj_b = (b.get('subject_name') or '').strip().lower()
            if subj_a and subj_a == subj_b and a['_dt'] != b['_dt']:
                _add_conflict(a['id'], 'subject'); _add_conflict(b['id'], 'subject')

    # ── Per-section daily limit violations ───────────────────────────────────
    # Group scheduled exams by (section, date)
    from collections import defaultdict as _dd
    sec_day_exams = _dd(list)   # (section, date_str) -> [exam, ...]
    for exam in scheduled_exams:
        sec = (exam.get('section') or '').strip()
        if sec:
            sec_day_exams[(sec, exam['_date_str'])].append(exam)

    for (sec, day), exams in sec_day_exams.items():
        major_exams = [e for e in exams if (e.get('subject_type') or 'Major') == 'Major']
        minor_exams = [e for e in exams if (e.get('subject_type') or 'Major') != 'Major']
        n_maj = len(major_exams)
        n_min = len(minor_exams)
        # Minor slots allowed = 4 - major count
        minor_limit = 4 - n_maj
        if n_maj > 3:
            for e in exams: _add_conflict(e['id'], 'daily_major')
        if n_min > minor_limit:
            for e in exams: _add_conflict(e['id'], 'daily_minor')
        if len(exams) > 4:
            for e in exams: _add_conflict(e['id'], 'daily_total')

    # Convert sets to sorted lists for template consumption
    conflict_reasons = {k: sorted(v) for k, v in conflict_reasons.items()}
    conflict_ids = sorted(list(conflict_ids))

    # Unique sections for dropdown filter
    all_sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip())))
    filter_section = request.args.get('section', '').strip()

    if filter_section:
        scheduled_exams = [e for e in scheduled_exams if e.get('section', '').strip() == filter_section]

    # Build timetable grid: unique sorted dates (columns) and time slots (rows)
    dates_set = sorted(set(e['_date_str'] for e in scheduled_exams))
    times_set = sorted(set(e['_time_str'] for e in scheduled_exams))

    # timetable[time_str][date_str] = list of exams
    timetable = defaultdict(lambda: defaultdict(list))
    for exam in scheduled_exams:
        timetable[exam['_time_str']][exam['_date_str']].append(exam)

    # date labels map
    date_labels = {}
    for e in scheduled_exams:
        date_labels[e['_date_str']] = e['_date_label']

    institutes = get_all_institutes()
    unread     = _get_unread(session['user_id'])
    return render_template("schedule.html",
                           timetable=timetable,
                           dates=dates_set,
                           date_labels=date_labels,
                           times=times_set,
                           scheduled_exams=scheduled_exams,
                           unscheduled=unscheduled,
                           failed=failed,
                           sched_count=len([e for e in all_exams if e['status'] == 'Scheduled']),
                           total=len(all_exams),
                           conflict_ids=conflict_ids,
                           conflict_reasons=conflict_reasons,
                           rooms=get_all_rooms(),
                           instructors=get_all_instructors(),
                           institutes=institutes,
                           unread_count=unread,
                           all_sections=all_sections,
                           filter_section=filter_section,
                           exam_term=get_exam_term()[0],
                           exam_semester=get_exam_term()[1])

@app.route("/api/available_resources", methods=["POST"])
def available_resources():
    guard = require_role('admin')
    if guard:
        return jsonify({'error': 'Not authorised'}), 403
    data = request.get_json(force=True)
    exam_id = int(data.get('exam_id', 0))
    dt_str = data.get('exam_datetime', '')
    duration = int(data.get('duration_minutes', 60))
    if not dt_str:
        return jsonify({'rooms': [], 'instructors': []})
    res = get_available_resources(exam_id, dt_str, duration)
    return jsonify(res)

@app.route("/check_edit_conflict", methods=["POST"])
def check_edit_conflict():
    guard = require_role('admin')
    if guard:
        return jsonify({'conflicts': ['Not authorised.']}), 403
    data         = request.get_json(force=True)
    exam_id      = int(data.get('exam_id', 0))
    new_room_id  = int(data.get('room_id', 0))
    new_inst_id  = int(data.get('instructor_id', 0))
    new_dt_str   = data.get('exam_datetime', '')
    duration     = int(data.get('duration_minutes', 60))
    conflicts    = check_edit_conflicts(exam_id, new_room_id, new_inst_id, new_dt_str, duration)
    return jsonify({'conflicts': conflicts})

@app.route("/edit_exam_schedule/<int:exam_id>", methods=["POST"])
def edit_exam_schedule(exam_id):
    guard = require_role('admin')
    if guard: return guard
    new_room_id  = int(request.form.get('room_id', 0))
    new_inst_id  = int(request.form.get('instructor_id', 0))
    new_dt_str   = request.form.get('exam_datetime', '')
    duration     = int(float(request.form.get('duration_hours', 1)) * 60)
    force        = request.form.get('force_save') == '1'
    if not force:
        conflicts = check_edit_conflicts(exam_id, new_room_id, new_inst_id, new_dt_str, duration)
        if conflicts:
            flash('Edit blocked: ' + ' | '.join(conflicts), 'danger')
            return redirect(url_for('schedule_view'))
    ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str)
    if ok:
        flash('Exam schedule updated.', 'success')
        # Also send email to the proctor as an extra channel
        try:
            exam = get_exam_by_id(exam_id)
            if exam and exam.get('instructor_id'):
                db = open_db()
                if db:
                    c = db.cursor(dictionary=True)
                    c.execute("SELECT u.email, u.full_name FROM users u WHERE u.instructor_id = %s AND u.role='proctor'",
                              (exam['instructor_id'],))
                    row = c.fetchone()
                    db.close()
                    if row and row.get('email'):
                        dt_str = new_dt_str.replace('T', ' ')
                        send_email_notification(
                            row['email'],
                            f"CCA Exam Schedule Updated — {exam['subject_name']}",
                            f"Dear {row['full_name']},\n\nYour proctoring assignment has been updated:\n"
                            f"Subject: {exam['subject_name']}\nNew Date/Time: {dt_str}\n\n"
                            f"CCA Exam Management System"
                        )
        except Exception as e:
            print(f"[Edit email error] {e}")
    else:
        flash('Failed to save changes.', 'danger')
    return redirect(url_for('schedule_view'))


# ── INSTITUTES ────────────────────────────────────────────────────────────────

@app.route("/institutes")
def institutes_page():
    guard = require_role('admin')
    if guard: return guard
    institutes = get_all_institutes()
    unread     = _get_unread(session['user_id'])
    return render_template("institutes.html", institutes=institutes, unread_count=unread)

@app.route("/institutes/add", methods=["POST"])
def add_institute_route():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").upper().strip()
    
    existing = get_all_institutes()
    if any(i['name'].lower() == name.lower() or i['code'].upper() == code for i in existing):
        flash(f"Warning: Institute name '{name}' or code '{code}' already exists.", "error")
        return redirect(url_for('institutes_page'))

    err = add_institute(
        name,
        request.form.get("code", "").upper(),
        request.form.get("capacity_default", 50)
    )
    if err:
        flash(f"Error: {err}", "danger")
    else:
        flash("Institute added.", "success")
    return redirect(url_for('institutes_page'))

@app.route("/institutes/<int:id>/edit", methods=["POST"])
def edit_institute_route(id):
    guard = require_role('admin')
    if guard: return guard
    edit_institute(id,
        request.form.get("name"),
        request.form.get("code", "").upper(),
        request.form.get("capacity_default", 50)
    )
    flash("Institute updated.", "success")
    return redirect(url_for('institutes_page'))

@app.route("/institutes/<int:id>/delete")
def delete_institute_route(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_institute(id)
    if err:
        flash(f"Cannot delete: {err}", "danger")
    else:
        flash("Institute deleted.", "success")
    return redirect(url_for('institutes_page'))

# ── SUBJECTS ──────────────────────────────────────────────────────────────────

@app.route("/subjects/link_content", methods=["POST"])
def link_content_route():
    guard = require_role('admin')
    if guard: return guard
    raw_ids = request.form.getlist("subject_ids")
    ids = []
    for v in raw_ids:
        # Support comma-separated values as well as multiple form fields
        for part in v.split(','):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
    # Deduplicate while preserving order
    seen = set()
    unique_ids = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique_ids.append(i)
    if len(unique_ids) < 2:
        flash("Select at least two different subjects to link.", "warning")
        return redirect(url_for('subjects_page'))
    # Link all selected subjects into one group by chaining pairwise links
    for i in range(1, len(unique_ids)):
        link_subjects_content_group(unique_ids[0], unique_ids[i])
    flash(f"{len(unique_ids)} subjects linked as identical content.", "success")
    return redirect(url_for('subjects_page'))

@app.route("/subjects/<int:id>/unlink")
def unlink_subject_route(id):
    guard = require_role('admin')
    if guard: return guard
    unlink_subject_content_group(id)
    flash("Subject removed from its content group.", "success")
    return redirect(url_for('subjects_page'))

@app.route("/subjects")
def subjects_page():
    guard = require_role('admin')
    if guard: return guard
    subjects       = get_all_subjects()
    institutes     = get_all_institutes()
    content_groups = get_subject_content_groups()
    unread         = _get_unread(session['user_id'])
    return render_template("subjects.html",
                           subjects=subjects, institutes=institutes,
                           content_groups=content_groups, unread_count=unread)

@app.route("/subjects/add", methods=["POST"])
def add_subject_route():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    
    existing = get_all_subjects()
    if any(s['code'].lower() == code.lower() for s in existing if s.get('code')):
        flash(f"Warning: Subject code '{code}' already exists.", "error")
        return redirect(url_for('subjects_page'))
        
    add_subject(
        name,
        request.form.get("code", ""),
        request.form.get("institute_id") or None,
        1 if request.form.get("is_common") else 0,
        request.form.get("content_group_id") or None
    )
    flash("Subject added.", "success")
    return redirect(url_for('subjects_page'))

@app.route("/subjects/<int:id>/edit", methods=["POST"])
def edit_subject_route(id):
    guard = require_role('admin')
    if guard: return guard
    edit_subject(id,
        request.form.get("name"),
        request.form.get("code", ""),
        request.form.get("institute_id") or None,
        1 if request.form.get("is_common") else 0,
        request.form.get("content_group_id") or None
    )
    flash("Subject updated.", "success")
    return redirect(url_for('subjects_page'))

@app.route("/subjects/<int:id>/delete")
def delete_subject_route(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_subject(id)
    if err:
        flash(f"Cannot delete: {err}", "danger")
    else:
        flash("Subject deleted.", "success")
    return redirect(url_for('subjects_page'))


@app.route("/subjects/bulk_delete", methods=["POST"])
def bulk_delete_subjects():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist('subject_ids')
    if not ids:
        flash("No subjects selected.", "warning")
        return redirect(url_for('subjects_page'))
    deleted, errors = 0, []
    for sid in ids:
        try:
            err = delete_subject(int(sid))
            if err:
                errors.append(err)
            else:
                deleted += 1
        except Exception as e:
            errors.append(str(e))
    if deleted:
        flash(f"✅ {deleted} subject(s) deleted successfully.", "success")
    if errors:
        flash(f"⚠️ {len(errors)} subject(s) could not be deleted: " + "; ".join(errors), "warning")
    return redirect(url_for('subjects_page'))


@app.route("/subjects/import", methods=["POST"])
def import_subjects_route():
    guard = require_role('admin')
    if guard: return guard
    f = request.files.get("csv_file")
    if not f:
        flash("No file uploaded.", "danger")
        return redirect(url_for('subjects_page'))
    from system.importer import parse_subjects_csv
    rows, parse_errors = parse_subjects_csv(f.read())
    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    for r in rows:
        code = r.get('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
    ok, errors = bulk_import_subjects(rows)
    if parse_errors:
        flash(f"Parse errors: {'; '.join(parse_errors)}", "warning")
    flash(f"Imported {ok} subject(s). {len(errors)} error(s).", "success" if not errors else "warning")
    return redirect(url_for('subjects_page'))

# ── FACULTY MANAGEMENT ────────────────────────────────────────────────────────

@app.route("/faculty")
def faculty_page():
    guard = require_role('admin')
    if guard: return guard
    instructors    = get_all_instructors()
    institutes     = get_all_institutes()
    subjects       = get_all_subjects()
    period_summary = get_all_proctor_hours_summary()
    unread         = _get_unread(session['user_id'])
    return render_template("faculty.html",
                           instructors=instructors, institutes=institutes,
                           subjects=subjects, period_summary=period_summary,
                           unread_count=unread)

@app.route("/faculty/<int:id>/edit", methods=["POST"])
def faculty_edit(id):
    guard = require_role('admin')
    if guard: return guard
    edit_instructor(id,
        request.form.get("name"),
        request.form.get("institute_id") or None,
        request.form.get("building", ""),
        1 if request.form.get("is_pwd") else 0,
        request.form.get("subjects_taught", "")
    )
    flash("Instructor updated.", "success")
    return redirect(url_for('faculty_page'))

@app.route("/faculty/<int:id>/deactivate", methods=["POST"])
def faculty_deactivate(id):
    guard = require_role('admin')
    if guard: return guard
    deactivate_instructor(id)
    flash("Instructor deactivated.", "warning")
    return redirect(url_for('faculty_page'))

@app.route("/faculty/<int:id>/activate", methods=["POST"])
def faculty_activate(id):
    guard = require_role('admin')
    if guard: return guard
    activate_instructor(id)
    flash("Instructor activated.", "success")
    return redirect(url_for('faculty_page'))

@app.route("/admin/proctor_availability/<int:id>", methods=["GET", "POST"])
def admin_proctor_availability(id):
    guard = require_role('admin')
    if guard: return guard
    
    # Get instructor info
    db = open_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM instructors WHERE id = %s", (id,))
    instructor = cursor.fetchone()
    db.close()
    
    if not instructor:
        flash("Instructor not found.", "danger")
        return redirect(url_for('faculty_page'))
        
    if request.method == "POST":
        dates       = request.form.getlist("available_dates")
        start_times = request.form.getlist("start_times")
        end_times   = request.form.getlist("end_times")
        entries = []
        for i, d in enumerate(dates):
            st = start_times[i] if i < len(start_times) else '07:00'
            et = end_times[i] if i < len(end_times) else '20:00'
            entries.append({'date': d, 'start_time': st, 'end_time': et})
        save_proctor_availability(id, entries)
        flash(f"Availability saved for {instructor['name']}.", "success")
        return redirect(url_for('faculty_page'))

    saved_dates = get_proctor_availability_for(id)
    return render_template("admin_availability.html", instructor=instructor, saved_dates=saved_dates)

# ── IMPORT ────────────────────────────────────────────────────────────────────

@app.route("/import/rooms", methods=["POST"])
def import_rooms():
    guard = require_role('admin')
    if guard: return guard
    f = request.files.get("csv_file")
    if not f:
        flash("No file uploaded.", "danger")
        return redirect(url_for('dashboard') + '#rooms')
    from system.importer import parse_rooms_csv
    rows, parse_errors = parse_rooms_csv(f.read())
    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    for r in rows:
        code = r.pop('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
    ok, errors = bulk_import_rooms(rows)
    if parse_errors:
        flash(f"Parse warnings: {'; '.join(parse_errors)}", "warning")
    flash(f"Imported {ok} room(s). {len(errors)} skipped.", "success" if not errors else "warning")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/import/instructors", methods=["POST"])
def import_instructors():
    guard = require_role('admin')
    if guard: return guard
    f = request.files.get("csv_file")
    if not f:
        flash("No file uploaded.", "danger")
        return redirect(url_for('dashboard') + '#instructors')
    from system.importer import parse_instructors_csv
    rows, parse_errors = parse_instructors_csv(f.read())
    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    for r in rows:
        code = r.pop('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
    ok, errors = bulk_import_instructors(rows)
    if parse_errors:
        flash(f"Parse warnings: {'; '.join(parse_errors)}", "warning")
    flash(f"Imported {ok} instructor(s). {len(errors)} skipped.", "success" if not errors else "warning")
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/import/exams", methods=["POST"])
def import_exams():
    guard = require_role('admin')
    if guard: return guard
    f = request.files.get("csv_file")
    if not f:
        flash("No file uploaded.", "danger")
        return redirect(url_for('dashboard') + '#exams')
    from system.importer import parse_exams_csv
    rows, parse_errors = parse_exams_csv(f.read())
    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    subjects_by_code = {s['code'].upper(): s for s in get_all_subjects()}
    
    for r in rows:
        code = r.pop('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
        
        subj_code = r.pop('subject_code', '').upper()
        subj = subjects_by_code.get(subj_code)
        if subj:
            r['subject_id'] = subj['id']
            r['subject_name'] = subj['name']
        else:
            r['subject_id'] = None
            r['subject_name'] = r.get('subject_name') or subj_code # Fallback to CSV name, or code

    ok, errors = bulk_import_exams(rows)
    if parse_errors:
        flash(f"Parse warnings: {'; '.join(parse_errors)}", "warning")
    flash(f"Imported {ok} exam(s). {len(errors)} skipped.", "success" if not errors else "warning")
    return redirect(url_for('dashboard') + '#exams')

@app.route("/exams/bulk_delete", methods=["POST"])
def bulk_delete_exams_route():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist('exam_ids')
    if not ids:
        flash("No exams selected.", "warning")
        return redirect(url_for('dashboard') + '#exams')
    deleted, errors = bulk_delete_exams(ids)
    if deleted:
        flash(f"Deleted {deleted} exam(s) successfully.", "success")
    if errors:
        flash(f"{len(errors)} exam(s) could not be deleted.", "warning")
    return redirect(url_for('dashboard') + '#exams')

# ── EXPORT ────────────────────────────────────────────────────────────────────

@app.route("/export/schedule.pdf")
def export_schedule_pdf():
    guard = require_role('admin')
    if guard: return guard
    from system.exporter import export_schedule_pdf as _pdf
    all_exams = get_schedule_results()
    scheduled_exams = [e for e in all_exams if e['status'] == 'Scheduled']
    # Build conflict_ids
    conflict_ids = set()
    for i, a in enumerate(scheduled_exams):
        dt_a = a['exam_date_time']
        if isinstance(dt_a, str):
            dt_a = datetime.strptime(dt_a, "%Y-%m-%d %H:%M:%S")
        end_a = dt_a + timedelta(minutes=a['duration_minutes'] or 60)
        for b in scheduled_exams[i+1:]:
            dt_b = b['exam_date_time']
            if isinstance(dt_b, str):
                dt_b = datetime.strptime(dt_b, "%Y-%m-%d %H:%M:%S")
            end_b = dt_b + timedelta(minutes=b['duration_minutes'] or 60)
            if dt_a < end_b and dt_b < end_a and a.get('room_id') == b.get('room_id'):
                conflict_ids.add(a['id']); conflict_ids.add(b['id'])
    # Group by date
    grouped = defaultdict(list)
    for exam in scheduled_exams:
        dt = exam['exam_date_time']
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    pdf_bytes = _pdf(sorted_groups, conflict_ids)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='exam_schedule.pdf')

@app.route("/export/absence_report.pdf")
def export_absence_pdf():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    from system.exporter import export_proctor_report_pdf
    absence = get_proctor_absence_report()
    hours   = get_all_proctor_hours_summary()
    pdf_bytes = export_proctor_report_pdf(hours, absence)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='proctor_report.pdf')

@app.route("/export/collection_report.pdf")
def export_collection_pdf():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    from system.exporter import export_collection_report_pdf
    data = get_exam_collection_status()
    pdf_bytes = export_collection_report_pdf(data)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='collection_report.pdf')

# ── REPORTS ───────────────────────────────────────────────────────────────────

@app.route("/reports")
def reports_page():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    absence   = get_proctor_absence_report(date_from or None, date_to or None)
    assignment = get_assignment_report()
    scheduling = get_scheduling_report()
    unread     = _get_unread(session['user_id'])
    return render_template("reports.html",
                           absence_report=absence,
                           assignment_report=assignment,
                           scheduling_report=scheduling,
                           date_from=date_from, date_to=date_to,
                           unread_count=unread)

# ── SETTINGS ──────────────────────────────────────────────────────────────────

@app.route("/settings")
def settings_page():
    guard = require_role('admin')
    if guard: return guard
    settings = get_system_settings()
    unread   = _get_unread(session['user_id'])
    return render_template("settings.html", settings=settings, unread_count=unread)

@app.route("/settings/save", methods=["POST"])
def settings_save():
    guard = require_role('admin')
    if guard: return guard
    
    def get_int(key, default):
        val = request.form.get(key, "").strip()
        return int(val) if val else default

    def get_float(key, default):
        val = request.form.get(key, "").strip()
        return float(val) if val else default

    save_system_settings(
        day_start=request.form.get("day_start", "07:00"),
        day_end=request.form.get("day_end", "20:00"),
        slot_interval_min=get_int("slot_interval_min", 60),
        max_proctor_hrs=get_int("max_consecutive_proctor_hrs", 3),
        travel_buffer_min=get_int("travel_buffer_min", 15),
        smtp_host=request.form.get("smtp_host", ""),
        smtp_port=get_int("smtp_port", 587),
        smtp_user=request.form.get("smtp_user", ""),
        smtp_password=request.form.get("smtp_password", ""),
        smtp_from=request.form.get("smtp_from", ""),
        smtp_use_tls=1 if request.form.get("smtp_use_tls") else 0,
        major_duration_hrs=get_float("major_duration_hrs", 2.0),
        minor_duration_hrs=get_float("minor_duration_hrs", 1.0)
    )
    
    # Auto-update existing exams to match the new duration defaults
    major_min = int(get_float("major_duration_hrs", 2.0) * 60)
    minor_min = int(get_float("minor_duration_hrs", 1.0) * 60)
    from system.database import open_db
    db = open_db()
    if db:
        try:
            cur = db.cursor()
            cur.execute("UPDATE exams SET duration_minutes=%s WHERE subject_type='Major'", (major_min,))
            cur.execute("UPDATE exams SET duration_minutes=%s WHERE subject_type='Minor'", (minor_min,))
            db.commit()
        except Exception as e:
            print("Auto-update exams error:", e)
        finally:
            db.close()

    _configure_mail()
    flash("Settings saved successfully.", "success")
    return redirect(url_for('settings_page'))

@app.route("/settings/test_email", methods=["POST"])
def test_email():
    guard = require_role('admin')
    if guard: return guard
    to = request.form.get("test_to", "")
    if not to:
        flash("Enter a recipient email address.", "warning")
        return redirect(url_for('settings_page'))
    try:
        # Instead of hanging the server with Flask-Mail, let's manually test the connection with a 5-second timeout
        import smtplib
        import socket
        s = get_system_settings()
        host = s.get('smtp_host', '')
        port = int(s.get('smtp_port') or 587)
        user = s.get('smtp_user', '')
        password = s.get('smtp_password', '')
        use_tls = bool(s.get('smtp_use_tls', 1))
        
        # Test TCP connection first
        try:
            socket.create_connection((host, port), timeout=5)
        except Exception as e:
            flash(f"Connection blocked or timed out (Port {port} might be blocked by your ISP or firewall): {e}", "danger")
            return redirect(url_for('settings_page'))
            
        # Try full SMTP handshake
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=5)
            server.ehlo()
        else:
            server = smtplib.SMTP(host, port, timeout=5)
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
        server.login(user, password)
        
        # If we reach here, connection works! Send the email.
        msg = f"Subject: CCA Exam Management - Test Email\n\nThis is a test email. SMTP works!"
        server.sendmail(user, [to], msg)
        server.quit()
        
        flash(f"Test email successfully sent to {to}!", "success")
    except smtplib.SMTPAuthenticationError:
        flash("SMTP Authentication Failed. Check your App Password.", "danger")
    except Exception as e:
        flash(f"SMTP Error: {e}", "danger")
        
    return redirect(url_for('settings_page'))
    try:
        _configure_mail()
        msg = MailMessage(
            subject="CCA Exam Management — Test Email",
            recipients=[to],
            body="This is a test email from the CCA Exam Management System. SMTP is configured correctly."
        )
        mail.send(msg)
        flash(f"Test email sent to {to}.", "success")
    except Exception as e:
        flash(f"Failed to send email: {e}", "danger")
    return redirect(url_for('settings_page'))

# ── CHANGE PASSWORD (Admin) ───────────────────────────────────────────────────

@app.route("/admin/change_password/<int:user_id>", methods=["POST"])
def admin_change_password(user_id):
    guard = require_role('admin')
    if guard: return guard
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    redirect_to = request.form.get("redirect_to", "students_page")
    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for(redirect_to))
    if new_password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for(redirect_to))
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c = db.cursor(dictionary=True)
            c.execute("SELECT full_name, role FROM users WHERE id = %s", (user_id,))
            user = c.fetchone()
            if not user or user['role'] not in ('student', 'proctor'):
                flash("User not found or not allowed.", "danger")
                return redirect(url_for(redirect_to))
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            db.commit()
            flash(f"✅ Password changed for {user['full_name']}.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for(redirect_to))

# ── STUDENTS (Admin-accessible) ───────────────────────────────────────────────

@app.route("/students")
def students_page():
    guard = require_role('admin')
    if guard: return guard
    pending_students = get_pending_users()
    all_students     = get_all_students()
    institutes       = get_all_institutes()
    unread           = _get_unread(session['user_id'])
    pending_count    = len(pending_students)
    return render_template("students.html",
                           pending_students=pending_students,
                           all_students=all_students,
                           institutes=institutes,
                           unread_count=unread,
                           pending_count=pending_count)

@app.route("/students/approve/<int:id>", methods=["POST"])
def admin_approve_student(id):
    guard = require_role('admin')
    if guard: return guard
    approve_student(id)
    flash("✅ Student account approved. They have been notified.", "success")
    return redirect(url_for('students_page'))

@app.route("/students/reject/<int:id>", methods=["POST"])
def admin_reject_student(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_user(id)
    if err:
        flash(f"Could not reject: {err}", "danger")
    else:
        flash("Student registration rejected and removed.", "success")
    return redirect(url_for('students_page'))

@app.route("/students/deactivate/<int:id>", methods=["POST"])
def admin_deactivate_student(id):
    guard = require_role('admin')
    if guard: return guard
    deactivate_student(id)
    flash("Student account deactivated.", "warning")
    return redirect(url_for('students_page'))

@app.route("/students/reactivate/<int:id>", methods=["POST"])
def admin_reactivate_student(id):
    guard = require_role('admin')
    if guard: return guard
    approve_student(id)   # approve_student sets is_active=1 and notifies
    flash("✅ Student account reactivated.", "success")
    return redirect(url_for('students_page'))

@app.route("/students/bulk_action", methods=["POST"])
def students_bulk_action():
    guard = require_role('admin')
    if guard: return guard
    action   = request.form.get('bulk_action', '')
    ids_raw  = request.form.getlist('selected_ids')
    try:
        user_ids = [int(i) for i in ids_raw if i.strip().isdigit()]
    except Exception:
        user_ids = []
    if not user_ids:
        flash("No students selected.", "warning")
        return redirect(url_for('students_page'))
    if action == 'deactivate':
        bulk_deactivate_students(user_ids)
        flash(f"⛔ {len(user_ids)} student(s) deactivated.", "warning")
    elif action == 'delete':
        bulk_delete_students(user_ids)
        flash(f"🗑 {len(user_ids)} student(s) deleted.", "danger")
    elif action == 'approve':
        for uid in user_ids:
            approve_student(uid)
        flash(f"✅ {len(user_ids)} student(s) approved.", "success")
    else:
        flash("Unknown action.", "danger")
    return redirect(url_for('students_page'))

# ── SUPER ADMIN ───────────────────────────────────────────────────────────────

@app.route("/super_admin")
def super_admin_page():
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    users            = get_all_users()
    pending_students = get_pending_users()
    institutes       = get_all_institutes()
    unread           = _get_unread(session['user_id'])
    return render_template("super_admin.html",
                           users=users,
                           pending_students=pending_students,
                           institutes=institutes,
                           roles=['admin', 'proctor', 'student', 'secretary'],
                           unread_count=unread)

@app.route("/super_admin/approve_student/<int:id>", methods=["POST"])
def approve_student_route(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    approve_student(id)
    flash("Student account approved and notified.", "success")
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/reject_student/<int:id>", methods=["POST"])
def reject_student_route(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    err = delete_user(id)
    if err:
        flash(f"Could not reject: {err}", "danger")
    else:
        flash("Student registration rejected and removed.", "success")
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/edit_user/<int:id>", methods=["POST"])
def super_edit_user(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    try:
        full_name    = request.form.get("full_name", "").strip()
        email        = request.form.get("email", "").strip()
        role         = request.form.get("role", "student").strip()
        section      = request.form.get("section", "").strip()
        institute_id = request.form.get("institute_id") or None
        is_sa        = 1 if request.form.get("is_super_admin") else 0

        # Validate role
        if role not in ("admin", "secretary", "proctor", "student"):
            flash("Invalid role selected.", "danger")
            return redirect(url_for('super_admin_page'))

        # Update local DB
        update_user(id, full_name, email, role, section, institute_id, is_sa)

        # Sync email change to Firebase if email changed
        from system.database import get_user_by_id
        db = open_db()
        if db:
            try:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT email FROM users WHERE id = %s", (id,))
                current = cursor.fetchone()
            finally:
                db.close()

        # Sync display name to Firebase
        try:
            from firebase_admin import auth as fb_auth
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.update_user(fb_user.uid, display_name=full_name)
        except Exception as fb_err:
            print(f"Firebase sync skipped: {fb_err}")

        flash(f"User '{full_name}' updated successfully to role '{role}'.", "success")
    except Exception as e:
        flash(f"Error updating user: {str(e)}", "danger")
    return redirect(url_for('super_admin_page'))


@app.route("/super_admin/update_email", methods=["POST"])
def super_update_email():
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    
    new_email = request.form.get("new_email", "").strip()
    if not new_email.endswith("@cca.edu.ph"):
        flash("Email must be a valid @cca.edu.ph address.", "danger")
        return redirect(url_for('super_admin_page'))
        
    user_id = session.get('user_id')
    db = open_db()
    if db:
        try:
            c = db.cursor(dictionary=True)
            # Check if email is already used by someone else
            c.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, user_id))
            if c.fetchone():
                flash("That email is already in use.", "danger")
                return redirect(url_for('super_admin_page'))
                
            # Get current email to find Firebase user
            c.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            current_user = c.fetchone()
            
            if current_user:
                # 1. Update Firebase
                from firebase_admin import auth as fb_auth
                try:
                    fb_user = fb_auth.get_user_by_email(current_user['email'])
                    fb_auth.update_user(fb_user.uid, email=new_email)
                except fb_auth.UserNotFoundError:
                    # If not in firebase for some reason, create them? Or skip.
                    pass
                except Exception as fb_err:
                    flash(f"Cloud Sync Error: {fb_err}", "danger")
                    return redirect(url_for('super_admin_page'))
                
                # 2. Update Local DB
                c.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
                db.commit()
                flash("Superadmin email has been successfully updated! Password resets will now go to this new address.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/delete_user/<int:id>", methods=["POST"])
def super_delete_user(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    if id == session.get('user_id'):
        flash("Cannot delete your own account.", "danger")
        return redirect(url_for('super_admin_page'))
    err = delete_user(id)
    if err:
        flash(f"Cannot delete: {err}", "danger")
    else:
        flash("User deleted.", "success")
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/reset_password/<int:id>", methods=["POST"])
def super_reset_password(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    new_password = request.form.get("new_password", "").strip()
    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for('super_admin_page'))
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c = db.cursor()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, id))
            db.commit()
            flash("Password reset successfully.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))

# ── PROCTOR DASHBOARD ─────────────────────────────────────────────────────────

@app.route("/proctor")
def proctor_dashboard():
    guard = require_role('proctor')
    if guard: return guard
    instructor_id = session.get('instructor_id')
    exams = get_proctor_exams(instructor_id) if instructor_id else []
    saved_dates = get_proctor_availability_for(instructor_id) if instructor_id else []
    total_hours = get_proctor_total_hours(instructor_id) if instructor_id else 0.0
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt: continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        exam['time'] = dt.strftime("%I:%M %p")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    period_start, period_end = get_exam_period()
    period_dates = []
    if period_start and period_end:
        cur = period_start
        while cur <= period_end:
            period_dates.append(str(cur))
            cur += timedelta(days=1)
    unread = _get_unread(session['user_id'])
    return render_template("proctor_dashboard.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           saved_dates=saved_dates,
                           period_dates=period_dates,
                           period_start=str(period_start) if period_start else '',
                           period_end=str(period_end) if period_end else '',
                           total_hours=total_hours,
                           unread_count=unread)



@app.route("/proctor/report_absence", methods=["POST"])
def proctor_report_absence():
    guard = require_role('proctor')
    if guard: return guard
    instructor_id = session.get('instructor_id')
    exam_id       = request.form.get("exam_id")
    reason        = request.form.get("reason", "").strip()
    if not exam_id:
        flash("Select an exam.", "warning")
        return redirect(url_for('proctor_dashboard'))
    record_proctor_absence(instructor_id, int(exam_id), reason, session['user_id'])
    flash("Absence reported.", "info")
    # Notify admin
    create_notification_for_role('admin',
        f"Proctor Absence: {session['full_name']}",
        f"{session['full_name']} reported an absence for exam #{exam_id}. Reason: {reason or 'Not specified'}.")
    return redirect(url_for('proctor_dashboard'))

# ── RELIEVERS ─────────────────────────────────────────────────────────────────

@app.route("/relievers")
def relievers_page():
    guard = require_role('admin')
    if guard: return guard
    relievers  = get_all_relievers()
    exams      = get_all_exams()
    instructors = get_active_instructors()
    unread     = _get_unread(session['user_id'])
    return render_template("faculty.html",  # reuse faculty template with extra context
                           relievers=relievers, exams=exams,
                           instructors=instructors,
                           institutes=get_all_institutes(),
                           subjects=get_all_subjects(),
                           period_summary=get_all_proctor_hours_summary(),
                           unread_count=unread)

@app.route("/relievers/add", methods=["POST"])
def add_reliever_route():
    guard = require_role('admin')
    if guard: return guard
    exam_id       = request.form.get("exam_id")
    instructor_id = request.form.get("instructor_id")
    reason        = request.form.get("reason", "")
    if exam_id and instructor_id:
        add_reliever(int(exam_id), int(instructor_id), reason)
        flash("Reliever assigned.", "success")
        # Notify the reliever
        db = open_db()
        if db:
            try:
                c = db.cursor(dictionary=True)
                c.execute("SELECT u.email, u.full_name FROM users u WHERE u.instructor_id = %s",
                          (instructor_id,))
                row = c.fetchone()
                if row:
                    send_email_notification(row['email'],
                        "CCA — You have been assigned as a Reliever",
                        f"Dear {row['full_name']},\n\nYou have been assigned as a reliever proctor for exam #{exam_id}.\n"
                        f"Reason: {reason or 'Not specified'}\n\nPlease log in for details.\n\nCCA Exam Management System")
            finally:
                db.close()
    else:
        flash("Select both exam and instructor.", "warning")
    return redirect(url_for('faculty_page'))

@app.route("/relievers/remove/<int:id>")
def remove_reliever_route(id):
    guard = require_role('admin')
    if guard: return guard
    remove_reliever(id)
    flash("Reliever removed.", "success")
    return redirect(url_for('faculty_page'))

# ── SECRETARY ─────────────────────────────────────────────────────────────────

@app.route("/secretary")
def secretary_dashboard():
    guard = require_role('secretary', 'admin')
    if guard: return guard
    # Admins see all institutes; secretaries see only their own
    inst_id     = None if session.get('role') == 'admin' else session.get('institute_id')
    exams       = get_exam_collection_status(institute_id=inst_id)
    instructors = get_active_instructors()
    stats       = get_collection_stats(institute_id=inst_id)
    unread      = _get_unread(session['user_id'])
    return render_template("secretary.html",
                           exams=exams, instructors=instructors,
                           stats=stats, unread_count=unread,
                           institute_id=inst_id)

@app.route("/secretary/collect/<int:exam_id>", methods=["POST"])
def secretary_collect(exam_id):
    guard = require_role('secretary', 'admin')
    if guard: return guard
    instructor_id = request.form.get("collected_by_instructor_id") or None
    notes         = request.form.get("notes", "")
    mark_exam_collected(exam_id, instructor_id, notes)
    flash("Marked as collected.", "success")
    return redirect(url_for('secretary_dashboard'))

@app.route("/secretary/return/<int:exam_id>", methods=["POST"])
def secretary_return(exam_id):
    guard = require_role('secretary', 'admin')
    if guard: return guard
    notes = request.form.get("notes", "")
    mark_exam_returned(exam_id, notes)
    flash("Marked as returned.", "success")
    return redirect(url_for('secretary_dashboard'))

@app.route("/secretary/change_password", methods=["POST"])
def secretary_change_password():
    guard = require_role('secretary', 'admin')
    if guard: return guard

    current_password = request.form.get("current_password", "").strip()
    new_password     = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # Validation
    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "danger")
        return redirect(url_for('secretary_dashboard'))
    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for('secretary_dashboard'))
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('secretary_dashboard'))

    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            c = db.cursor(dictionary=True)
            c.execute("SELECT id, full_name, password FROM users WHERE id = %s", (session['user_id'],))
            user = c.fetchone()
            if not user:
                flash("User not found.", "danger")
                return redirect(url_for('secretary_dashboard'))

            # Verify current password
            try:
                current_ok = _bcrypt.checkpw(current_password.encode(), user['password'].encode())
            except ValueError:
                current_ok = (current_password == user['password'])

            if not current_ok:
                flash("Current password is incorrect.", "danger")
                return redirect(url_for('secretary_dashboard'))

            # Save new hashed password
            new_hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed, session['user_id']))
            db.commit()
            flash("✅ Password changed successfully.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('secretary_dashboard'))

# ── PROCTOR ABSENCE (Admin view) ──────────────────────────────────────────────

@app.route("/admin/report_absence", methods=["POST"])
def admin_report_absence():
    guard = require_role('admin')
    if guard: return guard
    instructor_id = request.form.get("instructor_id")
    exam_id       = request.form.get("exam_id")
    reason        = request.form.get("reason", "")
    if instructor_id and exam_id:
        record_proctor_absence(int(instructor_id), int(exam_id), reason, session['user_id'])
        flash("Absence recorded.", "info")
    else:
        flash("Select instructor and exam.", "warning")
    return redirect(url_for('reports_page'))

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@app.route("/notifications")
def notifications_page():
    guard = require_login()
    if guard: return guard
    notifs = get_notifications(session['user_id'])
    unread = _get_unread(session['user_id'])
    return render_template("notifications.html",
                           notifications=notifs, unread_count=unread)

@app.route("/notifications/mark_read/<int:id>", methods=["POST"])
def mark_read(id):
    guard = require_login()
    if guard: return guard
    mark_notification_read(id, session['user_id'])
    return jsonify({'ok': True})

@app.route("/notifications/mark_all_read", methods=["POST"])
def mark_all_notifs_read():
    guard = require_login()
    if guard: return guard
    mark_all_read(session['user_id'])
    flash("All notifications marked as read.", "success")
    return redirect(url_for('notifications_page'))

# ── CHANGE OWN PASSWORD (Proctor / Student) ───────────────────────────────────

@app.route("/change_my_password", methods=["POST"])
def change_my_password():
    guard = require_login()
    if guard: return guard
    role = session.get('role')
    redirect_to = request.form.get("redirect_to", "")
    # Determine safe redirect target based on role
    safe_redirects = {
        'proctor': 'proctor_dashboard',
        'student': 'student_timetable',
    }
    fallback = safe_redirects.get(role, 'login')
    redirect_target = redirect_to if redirect_to in safe_redirects.values() else fallback

    new_password     = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for(redirect_target))
    if new_password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for(redirect_target))
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c = db.cursor()
            c.execute("UPDATE users SET password = %s WHERE id = %s",
                      (hashed, session['user_id']))
            db.commit()
            flash("✅ Password updated successfully.", "success")
        except Exception as e:
            flash(f"Error updating password: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for(redirect_target))

# ── STUDENT TIMETABLE ─────────────────────────────────────────────────────────



@app.route("/admin/batch_print_sections")
def admin_batch_print_sections():
    guard = require_role('admin')
    if guard: return guard
    
    all_exams = get_schedule_results()
    scheduled = [e for e in all_exams if e['status'] == 'Scheduled']
    
    # Group by section
    sections_dict = defaultdict(list)
    for exam in scheduled:
        sec = exam.get('section', '').strip()
        if sec:
            sections_dict[sec].append(exam)
            
    # For each section, build a grid
    section_grids = {}
    dates_set = set()
    times_set = set()
    
    for sec, exams in sections_dict.items():
        grid = defaultdict(lambda: defaultdict(list))
        for exam in exams:
            dt = exam['exam_date_time']
            if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            d_str = dt.strftime("%Y-%m-%d")
            t_str = dt.strftime("%H:%M")
            exam['_date_label'] = dt.strftime("%a %b %d")
            exam['datetime_raw'] = dt.strftime("%Y-%m-%dT%H:%M")
            exam['duration_minutes'] = exam.get('duration_minutes') or 60
            grid[t_str][d_str].append(exam)
            dates_set.add(d_str)
            times_set.add(t_str)
        section_grids[sec] = grid
        
    dates_list = sorted(list(dates_set))
    times_list = sorted(list(times_set))
    

    date_labels = {}
    for sec, exams in sections_dict.items():
        for e in exams:
            if '_date_label' in e:
                dt = e['exam_date_time']
                if isinstance(dt, str):
                            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                date_labels[dt.strftime("%Y-%m-%d")] = e['_date_label']

                
    return render_template("batch_print.html",
                           section_grids=section_grids,
                           dates=dates_list,
                           times=times_list,
                           date_labels=date_labels,
                           exam_term=get_exam_term()[0],
                           exam_semester=get_exam_term()[1])

@app.route("/admin/print_section")
def admin_print_section():
    guard = require_role('admin')
    if guard: return guard
    section = request.args.get('section', '').strip()
    if not section:
        flash("Please select a section.", "error")
        return redirect(url_for('schedule_view'))
    
    exams = get_public_timetable(section=section)
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt: continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        exam['time']     = dt.strftime("%I:%M %p")
        exam['time_end'] = (dt + timedelta(minutes=int(exam['duration_minutes'] or 60))).strftime("%I:%M %p")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    
    sorted_groups = sorted(grouped.items(), key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name="Admin Generated",
                           institute_name="City College of Angeles",
                           exam_term=get_exam_term()[0],
                           exam_semester=get_exam_term()[1])

@app.route("/timetable")
def student_timetable():
    guard = require_role('student')
    if guard: return guard
    section      = session.get('section', '')
    institute_id = session.get('institute_id')
    full_name    = session.get('full_name', 'Student')
    exams = get_public_timetable(section=section, institute_id=institute_id)
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt: continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        exam['time']     = dt.strftime("%I:%M %p")
        exam['time_end'] = (dt + timedelta(minutes=int(exam['duration_minutes'] or 60))).strftime("%I:%M %p")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    # Get institute name
    institute_name = ''
    if institute_id:
        all_inst = get_all_institutes()
        for i in all_inst:
            if i['id'] == institute_id:
                institute_name = i['name']
                break
    unread = _get_unread(session['user_id'])
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name=full_name,
                           institute_name=institute_name,
                           unread_count=unread)

# ── MISC ──────────────────────────────────────────────────────────────────────

@app.route("/clear-session")
def clear_session():
    session.clear()
    response = redirect(url_for('index'))
    response.delete_cookie('session')
    return response

# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=9999)

