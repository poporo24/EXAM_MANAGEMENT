"""
app.py â€” CCA Exam Management System v2
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
    save_exam_period, save_exam_term, get_exam_term, get_exam_period,
    # proctor availability
    get_proctor_availability, get_proctor_availability_for, save_proctor_availability,
    bulk_save_proctor_availability,
    get_proctor_exams,
    # timetable
    get_public_timetable, is_schedule_published, publish_schedule, unpublish_schedule,
    # relievers
    add_reliever, get_relievers_for_exam, get_all_relievers, remove_reliever,
    # secretary
    get_exam_collection_status, mark_exam_collected, mark_exam_returned,
    get_collection_stats,
    # absence
    record_proctor_absence, get_proctor_absence_report, get_absence_stats, clear_absence_reports,
    # notifications
    create_notification, get_notifications, get_unread_count, clear_all_notifications,
    mark_notification_read, mark_all_read, create_notification_for_role,
    # reports
    get_scheduling_report, get_assignment_report, get_student_exam_load_report,
    # archives
    create_exam_archive, get_exam_archives, get_exam_archive_by_id, delete_exam_archive, sync_archive_durations,
    # period & audit
    open_db, ensure_database_schema, log_audit_event,
)
from system.scheduler import run_scheduler
from system.logic import verify_login, is_super_admin, hash_password, validate_password_strength
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded

# â”€â”€ FLASK APP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


app = Flask(__name__, template_folder='template')
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
csrf = CSRFProtect(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2500 per day", "600 per hour"],
    storage_uri="memory://"
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cca_exam_management_secret_key_v2")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB max upload limit
    WTF_CSRF_TIME_LIMIT=7200  # 2 hours CSRF token validity
)

# Automatically ensure database schema (tables & columns) exists
try:
    ensure_database_schema()
except Exception as _schema_err:
    print(f"Warning: automatic database schema check encountered an error: {_schema_err}")

# â”€â”€ MAIL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _configure_mail():
    try:
        s = get_system_settings()
    except Exception:
        s = {}
    # Prioritize secure environment variables over database storage
    app.config['MAIL_SERVER']         = os.environ.get('SMTP_HOST') or s.get('smtp_host', '') or ''
    app.config['MAIL_PORT']           = int(os.environ.get('SMTP_PORT') or s.get('smtp_port') or 587)
    app.config['MAIL_USERNAME']       = os.environ.get('SMTP_USER') or s.get('smtp_user', '') or ''
    app.config['MAIL_PASSWORD']       = os.environ.get('SMTP_PASSWORD') or s.get('smtp_password', '') or ''
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('SMTP_FROM') or s.get('smtp_from', '') or ''
    app.config['MAIL_USE_TLS']        = bool(int(os.environ.get('SMTP_USE_TLS', s.get('smtp_use_tls', 1))))
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

# â”€â”€ HELPERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def require_login():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return None

def require_super_admin():
    guard = require_login()
    if guard:
        return guard
    if not session.get('is_super_admin'):
        flash("Access denied. Super Admin privileges required.", "danger")
        return _redirect_by_role()
    return None

@app.after_request
def add_security_and_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    # Security Headers (Addresses MED-03 Clickjacking & MIME-Sniffing)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Auto-inject CSRF meta tag and auto-protection script into HTML responses
    if response.mimetype == 'text/html' and response.status_code == 200:
        html = response.get_data(as_text=True)
        if '</head>' in html and 'csrf.js' not in html:
            token = generate_csrf()
            csrf_tags = (
                f'<meta name="csrf-token" content="{token}">\n'
                f'<script src="/static/js/csrf.js"></script>\n'
            )
            response.set_data(html.replace('</head>', f'{csrf_tags}</head>', 1))
    return response

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'CSRF token missing or invalid', 'message': str(e.description)}), 400
    flash(f"Security notice: {e.description}. Please refresh the page and try again.", "warning")
    return redirect(request.referrer or url_for('login'))

@app.errorhandler(RateLimitExceeded)
def handle_ratelimit_error(e):
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'Rate limit exceeded', 'message': 'Too many requests. Please slow down.'}), 429
    flash("Too many requests from your network. Please wait a moment before trying again.", "warning")
    return redirect(request.referrer or url_for('login'))

@app.template_filter('clean_hours')
def clean_hours_filter(val):
    if val is None or val == '':
        return 0
    try:
        f = float(val)
        return int(f) if f.is_integer() or f % 1 == 0 else round(f, 1)
    except (ValueError, TypeError):
        return val

@app.template_filter('exam_time_range')
def exam_time_range_filter(dt, duration=60):
    if not dt:
        return 'TBD'
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M")
            except Exception:
                return dt
    try:
        dur = int(duration or 60)
    except (ValueError, TypeError):
        dur = 60
    end_dt = dt + timedelta(minutes=dur)
    return f"{dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"

@app.template_filter('exam_datetime_range')
def exam_datetime_range_filter(dt, duration=60):
    if not dt:
        return 'TBD'
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M")
            except Exception:
                return dt
    try:
        dur = int(duration or 60)
    except (ValueError, TypeError):
        dur = 60
    end_dt = dt + timedelta(minutes=dur)
    return f"{dt.strftime('%b %d, %Y')} • {dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}" 

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

@app.context_processor
def inject_notifications_unread():
    uid = session.get('user_id')
    role = session.get('role')
    unread = _get_unread(uid) if uid else 0
    pending_count = 0
    if role in ('admin', 'super_admin') or session.get('is_super_admin'):
        try:
            pending_count = len(get_pending_users())
        except Exception:
            pending_count = 0
    return {'unread_count': unread, 'pending_count': pending_count}

# â”€â”€ AUTH â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
@limiter.limit("5 per minute", methods=["POST"])
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
@limiter.limit("5 per minute", methods=["POST"])
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
        
        is_valid, err_msg = validate_password_strength(new_password)
        if not is_valid:
            flash(err_msg, "error")
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
@limiter.limit("15 per minute", methods=["POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session and session.get('role'):
            return _redirect_by_role()
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        # Toggle Demo Accounts card on login page (defaults to False for security)
        show_demo = os.environ.get('SHOW_DEMO_ACCOUNTS', 'False').lower() in ('true', '1', 'yes')
        return render_template("login.html", sections=sections, show_demo=show_demo)

    
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
        session['email']          = user.get('email', email)
        session['instructor_id']  = user.get('instructor_id')
        session['is_super_admin'] = bool(user.get('is_super_admin', 0))
        session['section']        = user.get('section', '')
        session['institute_id']   = user.get('institute_id')
        log_audit_event('AUTH_LOGIN_SUCCESS', f"User authenticated as {user.get('role')}", user_id=user['id'], user_name=user['full_name'], user_role=user.get('role'), ip_address=request.remote_addr)
        return _redirect_by_role()
    log_audit_event('AUTH_LOGIN_FAILED', f"Failed login attempt for: {email}", ip_address=request.remote_addr)
    flash("Invalid email or password.", "error")
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    log_audit_event('AUTH_LOGOUT', "User logged out", user_id=session.get('user_id'), user_name=session.get('full_name'), user_role=session.get('role'), ip_address=request.remote_addr)
    session.clear()
    return redirect(url_for('login'))

# â”€â”€ REGISTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/terms")
def terms_page():
    return render_template("terms.html")

@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

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
@limiter.limit("10 per minute")
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
        
    is_valid, err_msg = validate_password_strength(password)
    if not is_valid:
        flash(err_msg, "danger")
        return redirect(url_for('register_page'))

    if not full_name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('register_page'))
        
    # Check if user already exists in MySQL
    user_exists = get_user_by_email(email)
    if user_exists:
        flash("That email is already registered.", "danger")
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

# â”€â”€ ADD ROUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/add_exam", methods=["POST"])
def add_exam_route():
    guard = require_role('admin')
    if guard: return guard
    subject_id = request.form.get("subject_id")
    section = request.form.get("section", "").strip().upper()
    raw_type = request.form.get("subject_type", "Major").strip()
    st_norm = raw_type.lower()
    subject_type = 'Minor' if st_norm in ('minor', 'laboratory', 'lab') else 'Major'
    
    dur_hrs = request.form.get("duration_hours")
    if dur_hrs:
        try:
            duration_minutes = int(round(float(dur_hrs) * 60))
        except (ValueError, TypeError):
            duration_minutes = 180 if subject_type == 'Major' else 60
    else:
        duration_minutes = 180 if subject_type == 'Major' else 60

    institute_id = request.form.get("institute_id") or None
    
    subject_name = ""
    if subject_id:
        from system.database import get_subject_by_id
        sub = get_subject_by_id(subject_id)
        if sub:
            subject_name = sub.get('name') or sub.get('code') or ''

    add_exam(subject_name, section, subject_type, duration_minutes, institute_id, subject_id)
    flash(f"Exam '{subject_name}' ({section}) added successfully.", "success")
    return redirect(url_for('dashboard') + '#exams')

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

@app.route("/edit_room/<int:id>", methods=["POST"])
@app.route("/rooms/<int:id>/edit", methods=["POST"])
def edit_room_route(id):
    guard = require_role('admin')
    if guard: return guard
    room_name = request.form.get("room_name", "").strip()
    try:
        capacity = int(request.form.get("capacity") or 0)
    except (ValueError, TypeError):
        capacity = 0
    building = request.form.get("building", "").strip()
    try:
        floor = int(request.form.get("floor") or 1)
    except (ValueError, TypeError):
        floor = 1
    institute_id = request.form.get("institute_id") or None
    is_pwd_accessible = 1 if request.form.get("is_pwd_accessible") else 0
    edit_room(id, room_name, capacity, building, floor, institute_id, is_pwd_accessible)
    flash(f"Room '{room_name}' updated successfully.", "success")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/delete_room/<int:id>", methods=["POST"])
@app.route("/rooms/<int:id>/delete", methods=["POST"])
def delete_room_route(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_room(id)
    if err:
        flash(f"Could not delete room: {err}", "danger")
    else:
        flash("Room deleted successfully.", "success")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/rooms/bulk_delete", methods=["POST"])
def rooms_bulk_delete():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist("room_ids")
    deleted, errors = 0, []
    for rid in ids:
        try:
            err = delete_room(int(rid))
            if err:
                errors.append(err)
            else:
                deleted += 1
        except Exception as e:
            errors.append(str(e))
    if deleted:
        flash(f"{deleted} room(s) deleted successfully.", "success")
    if errors:
        flash(f"{len(errors)} room(s) could not be deleted: {errors[0]}", "warning")
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/add_instructor", methods=["POST"])
def add_instructor_route():
    guard = require_role('admin')
    if guard: return guard
    
    last = request.form.get("last_name", "").strip()
    first = request.form.get("first_name", "").strip()
    middle = request.form.get("middle_name", "").strip()
    suffix = request.form.get("suffix", "").strip()
    
    if last and first:
        full_name = f"{last}, {first}"
        if middle:
            full_name += f" {middle[0]}." if len(middle) == 1 else f" {middle}"
        if suffix:
            full_name += f" {suffix}"
    else:
        full_name = request.form.get("name", "").strip()
        
    add_instructor(
        full_name,
        request.form.get("institute_id") or None,
        request.form.get("building", ""),
        1 if request.form.get("is_pwd") else 0,
        request.form.get("subjects_taught", "")
    )
    flash("Instructor added.", "success")
    return redirect(url_for('faculty_page'))

@app.route("/delete_instructor/<int:id>", methods=["POST"])
@app.route("/faculty/<int:id>/delete", methods=["POST"])
def remove_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_instructor(id)
    if err:
        flash(f"Could not delete instructor: {err}", "danger")
    else:
        flash("Instructor deleted successfully.", "success")
    return redirect(url_for('faculty_page'))

@app.route("/faculty/bulk_delete", methods=["POST"])
@app.route("/instructors/bulk_delete", methods=["POST"])
def faculty_bulk_delete():
    guard = require_role('admin')
    if guard: return guard
    ids = request.form.getlist("instructor_ids")
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
        flash(f"{deleted} instructor(s) deleted successfully.", "success")
    if errors:
        flash(f"{len(errors)} instructor(s) could not be deleted: " + "; ".join(errors), "warning")
    ref = request.referrer or ''
    if 'dashboard' in ref:
        return redirect(url_for('dashboard') + '#instructors')
    return redirect(url_for('faculty_page'))


@app.route("/delete_exam/<int:id>", methods=["POST"])
def remove_exam(id):
    guard = require_role('admin')
    if guard: return guard
    delete_exam(id)
    log_audit_event('EXAM_DELETE', f"Deleted exam ID {id}", user_id=session.get('user_id'), user_name=session.get('full_name'), user_role=session.get('role'), ip_address=request.remote_addr)
    flash('Exam deleted.', 'success')
    return redirect(url_for('dashboard') + '#exams')

@app.route("/delete_all_exams", methods=["POST"])
def remove_all_exams():
    guard = require_role('admin')
    if guard: return guard
    count = delete_all_exams()
    log_audit_event('EXAM_DELETE_ALL', f"Purged all {count} exams from system", user_id=session.get('user_id'), user_name=session.get('full_name'), user_role=session.get('role'), ip_address=request.remote_addr)
    flash(f' All {count} exam(s) deleted successfully.', 'success')
    return redirect(url_for('dashboard') + '#exams')

# â”€â”€ SCHEDULE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    guard = require_role('admin')
    if guard: return guard

    period_start_str = request.form.get("period_start")
    period_end_str   = request.form.get("period_end")
    day_start_str    = request.form.get("day_start")
    day_end_str      = request.form.get("day_end")
    
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
    
    settings = get_system_settings()
    if day_start_str and day_end_str:
        save_system_settings(
            day_start=day_start_str,
            day_end=day_end_str,
            slot_interval_min=settings.get('slot_interval_min', 60),
            max_proctor_hrs=settings.get('max_consecutive_proctor_hrs', 3.0),
            travel_buffer_min=settings.get('travel_buffer_min', 15),
            smtp_host=settings.get('smtp_host', ''),
            smtp_port=settings.get('smtp_port', 587),
            smtp_user=settings.get('smtp_user', ''),
            smtp_password=settings.get('smtp_password', ''),
            smtp_from=settings.get('smtp_from', ''),
            smtp_use_tls=settings.get('smtp_use_tls', 1),
            major_duration_hrs=settings.get('major_duration_hrs', 3.0),
            minor_duration_hrs=settings.get('minor_duration_hrs', 1.0),
            max_daily_proctor_hrs=settings.get('max_daily_proctor_hrs', 4.0)
        )
        settings = get_system_settings() # reload

    pending     = get_pending_exams()
    rooms       = get_all_rooms()
    instructors = get_active_instructors()
    booked      = get_already_scheduled_slots()
    proctor_av  = get_proctor_availability()
    settings    = get_system_settings()

    if not rooms:
        flash(" No rooms found. Add at least one room first.", "warning")
        return redirect(url_for('schedule_view'))
    if not instructors:
        flash(" No active instructors found.", "warning")
        return redirect(url_for('schedule_view'))
    if not pending:
        flash(" No pending exams to schedule.", "info")
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
                        f"CCA Exam Proctoring Assignment â€” {row['subject_name']}",
                        f"Dear {row['full_name']},\n\nYou have been assigned to proctor:\n"
                        f"Subject: {row['subject_name']} ({row['section'] or 'â€”'})\n"
                        f"Date/Time: {dt_str}\n\nPlease log in to view full details.\n\n"
                        f"CCA Exam Management System"
                    )
        except Exception as e:
            print(f"[Email batch error] {e}")
        finally:
            db.close()

    flash(f" Scheduled {len(result['scheduled'])} exam(s). "
          f"{len(result['failed'])} could not be placed.", "success")
    return redirect(url_for('schedule_view'))

@app.route("/reset_schedule", methods=["GET", "POST"])
def reset_schedule_route():
    guard = require_role('admin')
    if guard: return guard
    # Check if user requested archiving before resetting
    if request.form.get('archive_before_reset') == '1':
        term_tuple = get_exam_term()
        exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
        exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
        ok, res = create_exam_archive(
            academic_year="2025-2026",
            exam_term=exam_term,
            exam_semester=exam_semester,
            archive_title=None,
            notes="Automatically archived prior to schedule reset.",
            user_id=session.get('user_id'),
            user_name=session.get('full_name')
        )
        if ok:
            flash("Archived a snapshot of the current schedule before resetting.", "info")
    reset_schedule()
    session.pop('last_failed', None)
    session.pop('last_scheduled_count', None)
    flash('Schedule reset. All exams are back to Pending.', 'success')
    return redirect(url_for('schedule_view'))

@app.route("/schedule/publish", methods=["POST"])
def schedule_publish():
    guard = require_role('admin')
    if guard: return guard
    from system.database import publish_schedule
    ok, msg = publish_schedule(user_id=session.get('user_id'))
    if ok:
        flash("Exam timetable has been finalized and published! It is now live on Student and Proctor portals.", "success")
    else:
        flash(f"Failed to publish timetable: {msg}", "danger")
    return redirect(url_for('schedule_view'))

@app.route("/schedule/unpublish", methods=["POST"])
def schedule_unpublish():
    guard = require_role('admin')
    if guard: return guard
    from system.database import unpublish_schedule
    ok, msg = unpublish_schedule(user_id=session.get('user_id'))
    if ok:
        flash("Exam timetable has been reverted to Draft mode. It is now hidden from students, proctors, and secretaries.", "warning")
    else:
        flash(f"Failed to unpublish timetable: {msg}", "danger")
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
    
    resolved_info = ""
    if result['scheduled']:
        resolved_details = [f"{e.get('subject_name')} ({e.get('section')})" for e in result['scheduled']]
        resolved_info = " Resolved: " + ", ".join(resolved_details)

    if failed_ids:
        flash(f"Auto-resolve completed, but {len(failed_ids)} exam(s) could still not be scheduled.{resolved_info}", "warning")
    else:
        flash(f"All conflicts have been successfully auto-resolved!{resolved_info}", "success")
        
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
            dur = int(exam.get('duration_minutes') or 60)
            end_dt = dt + timedelta(minutes=dur)
            exam['_dt']          = dt
            exam['_end_dt']      = end_dt
            exam['_date_str']    = dt.strftime("%Y-%m-%d")          # for grouping
            exam['_time_str']    = dt.strftime("%H:%M")             # row key
            exam['time']         = dt.strftime("%I:%M %p")
            exam['time_end']     = end_dt.strftime("%I:%M %p")
            exam['time_range']   = f"{exam['time']} - {exam['time_end']}"
            exam['_date_label']  = dt.strftime("%a %b %d")       # column header
            exam['datetime']     = dt.strftime("%b %d, %Y %I:%M %p")
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

    # â”€â”€ Per-section daily limit violations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    time_labels = {}
    for e in scheduled_exams:
        time_labels[e['_time_str']] = e['time']

    institutes = get_all_institutes()
    unread     = _get_unread(session['user_id'])
    return render_template("schedule.html",
                           timetable=timetable,
                           dates=dates_set,
                           date_labels=date_labels,
                           time_labels=time_labels,
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
                           exam_semester=get_exam_term()[1],
                           is_published=is_schedule_published())

@app.route("/api/auto_schedule_exam", methods=["POST"])
def api_auto_schedule_exam():
    guard = require_role('admin')
    if guard: return jsonify({})
    data = request.get_json(force=True)
    exam_id = int(data.get('exam_id', 0))
    duration = int(data.get('duration_minutes', 60))
    sync_all = bool(data.get('sync_all', False))
    
    from system.database import get_full_auto_schedule
    result = get_full_auto_schedule(exam_id, duration, sync_all=sync_all)
    return jsonify(result or {})

@app.route("/api/suggest_times", methods=["POST"])
def api_suggest_times():
    guard = require_role('admin')
    if guard: return jsonify([])
    data = request.get_json(force=True)
    exam_id = int(data.get('exam_id', 0))
    duration = int(data.get('duration_minutes', 60))
    room_id = int(data.get('room_id', 0))
    proctor_id = int(data.get('instructor_id', 0))
    
    from system.database import get_suggested_times
    suggestions = get_suggested_times(exam_id, duration, room_id, proctor_id)
    return jsonify({'suggestions': suggestions})

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

@app.route("/api/resource_availability", methods=["GET"])
def api_resource_availability():
    guard = require_role('admin', 'secretary', 'proctor')
    if guard:
        return jsonify({'error': 'Not authorised'}), 403
    res_type = request.args.get('type', '').strip().lower()
    res_id   = request.args.get('id', '').strip()
    if not res_type or not res_id or not res_id.isdigit():
        return jsonify({'error': 'Invalid resource parameters'}), 400
    
    from system.database import get_resource_schedule_details
    details = get_resource_schedule_details(res_type, int(res_id))
    if not details:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(details)


@app.route("/api/sister_sections", methods=["GET"])
def get_sister_sections():
    guard = require_role('admin')
    if guard:
        return jsonify({'error': 'Not authorised'}), 403
    exam_id = request.args.get('exam_id', type=int)
    from system.database import open_db
    db = open_db()
    if not db:
        return jsonify({'sections': []})
    try:
        c = db.cursor(dictionary=True)
        c.execute("SELECT subject_name FROM exams WHERE id=%s", (exam_id,))
        ex = c.fetchone()
        if not ex or not ex.get('subject_name'): return jsonify({'sections': []})
        # All sections taking this exam (including the one being edited)
        c.execute("""
            SELECT e.id, e.subject_name, e.section, e.room_id, e.instructor_id, e.exam_date_time,
                   r.room_name, i.name AS instructor_name
            FROM exams e
            LEFT JOIN rooms r       ON r.id = e.room_id
            LEFT JOIN instructors i ON i.id = e.instructor_id
            WHERE UPPER(REPLACE(e.subject_name,' ',''))=UPPER(REPLACE(%s,' ',''))
            ORDER BY e.section
        """, (ex['subject_name'],))
        rows = c.fetchall()
        for r in rows:
            r['is_current'] = (r['id'] == exam_id)
            dt = r.get('exam_date_time')
            r['exam_date_time'] = dt.strftime('%b %d, %Y %I:%M %p') if dt else None
        return jsonify({'sections': rows})
    finally:
        db.close()

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
    sync_all     = request.form.get('sync_all_sections') in ['on', '1']
    
    if not force:
        conflicts = check_edit_conflicts(exam_id, new_room_id, new_inst_id, new_dt_str, duration)
        if conflicts:
            flash('Edit blocked: ' + ' | '.join(conflicts), 'danger')
            return redirect(url_for('schedule_view'))
    ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str, sync_all=sync_all, form_data=request.form)
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
                            f"CCA Exam Schedule Updated â€” {exam['subject_name']}",
                            f"Dear {row['full_name']},\n\nYour proctoring assignment has been updated:\n"
                            f"Subject: {exam['subject_name']}\nNew Date/Time: {dt_str}\n\n"
                            f"CCA Exam Management System"
                        )
        except Exception as e:
            print(f"[Edit email error] {e}")
    else:
        flash('Failed to save changes.', 'danger')
    return redirect(url_for('schedule_view'))


# â”€â”€ INSTITUTES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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

@app.route("/institutes/<int:id>/delete", methods=["POST"])
def delete_institute_route(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_institute(id)
    if err:
        flash(f"Cannot delete: {err}", "danger")
    else:
        flash("Institute deleted.", "success")
    return redirect(url_for('institutes_page'))

# â”€â”€ SUBJECTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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

@app.route("/subjects/<int:id>/delete", methods=["POST"])
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
        flash(f" {deleted} subject(s) deleted successfully.", "success")
    if errors:
        flash(f" {len(errors)} subject(s) could not be deleted: " + "; ".join(errors), "warning")
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

# â”€â”€ FACULTY MANAGEMENT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/faculty")
def faculty_page():
    guard = require_role('admin')
    if guard: return guard
    instructors    = get_all_instructors()
    institutes     = get_all_institutes()
    subjects       = get_all_subjects()
    period_summary = get_all_proctor_hours_summary()
    unread         = _get_unread(session['user_id'])
    
    period_start, period_end = get_exam_period()
    exam_start = period_start.strftime('%Y-%m-%d') if period_start else ''
    exam_end   = period_end.strftime('%Y-%m-%d') if period_end else ''
    
    return render_template("faculty.html",
                           instructors=instructors, institutes=institutes,
                           subjects=subjects, period_summary=period_summary,
                           unread_count=unread,
                           exam_start=exam_start, exam_end=exam_end)

@app.route("/faculty/<int:id>/edit", methods=["POST"])
@app.route("/edit_instructor/<int:id>", methods=["POST"])
def faculty_edit(id):
    guard = require_role('admin')
    if guard: return guard
    
    last = request.form.get("last_name", "").strip()
    first = request.form.get("first_name", "").strip()
    middle = request.form.get("middle_name", "").strip()
    suffix = request.form.get("suffix", "").strip()
    
    if last and first:
        full_name = f"{last}, {first}"
        if middle:
            full_name += f" {middle[0]}." if len(middle) == 1 else f" {middle}"
        if suffix:
            full_name += f" {suffix}"
    else:
        full_name = request.form.get("name", "").strip()
        
    edit_instructor(id,
        full_name,
        request.form.get("institute_id") or None,
        request.form.get("building", ""),
        1 if request.form.get("is_pwd") else 0,
        request.form.get("subjects_taught", "")
    )
    flash("Instructor updated.", "success")
    ref = request.referrer or ''
    if 'dashboard' in ref:
        return redirect(url_for('dashboard') + '#instructors')
    return redirect(url_for('faculty_page'))

@app.route("/faculty/<int:id>/deactivate", methods=["POST"])
@app.route("/deactivate_instructor/<int:id>", methods=["POST"])
def faculty_deactivate(id):
    guard = require_role('admin')
    if guard: return guard
    deactivate_instructor(id)
    flash("Instructor deactivated.", "warning")
    ref = request.referrer or ''
    if 'dashboard' in ref:
        return redirect(url_for('dashboard') + '#instructors')
    return redirect(url_for('faculty_page'))

@app.route("/faculty/<int:id>/activate", methods=["POST"])
@app.route("/activate_instructor/<int:id>", methods=["POST"])
def faculty_activate(id):
    guard = require_role('admin')
    if guard: return guard
    activate_instructor(id)
    flash("Instructor activated.", "success")
    ref = request.referrer or ''
    if 'dashboard' in ref:
        return redirect(url_for('dashboard') + '#instructors')
    return redirect(url_for('faculty_page'))

@app.route("/admin/proctor_availability/<int:id>", methods=["GET", "POST"])
def admin_proctor_availability(id):
    guard = require_role('admin')
    if guard: return guard
    
    # Get instructor info
    db = open_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, inst.name as institute_name,
               (SELECT ROUND(COALESCE(SUM(duration_minutes)/60.0, 0), 1) FROM exams WHERE instructor_id = i.id AND status = 'Scheduled') as total_hours
        FROM instructors i LEFT JOIN institutes inst ON i.institute_id = inst.id WHERE i.id = %s
    """, (id,))
    instructor = cursor.fetchone()
    db.close()
    if instructor and instructor.get('total_hours') is not None:
        tot = float(instructor['total_hours'])
        instructor['total_hours'] = int(tot) if tot.is_integer() else round(tot, 1)
    
    if not instructor:
        flash("Instructor not found.", "danger")
        return redirect(url_for('faculty_page'))
        
    if request.method == "POST":
        dates       = request.form.getlist("available_dates")
        start_times = request.form.getlist("start_times")
        end_times   = request.form.getlist("end_times")
        entries = []
        for i, d in enumerate(dates):
            d_str = str(d).strip()
            if not d_str: continue
            st = start_times[i].strip() if i < len(start_times) and start_times[i].strip() else '07:00'
            et = end_times[i].strip() if i < len(end_times) and end_times[i].strip() else '20:00'
            entries.append({'date': d_str, 'start_time': st, 'end_time': et})
            
        save_proctor_availability(id, entries)
        
        # Check if also applying to additional instructors
        also_apply_ids = request.form.getlist("also_apply_ids")
        if request.form.get("apply_to_same_dept") == "1" and instructor.get('institute_id'):
            db = open_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id FROM instructors WHERE institute_id = %s AND id != %s AND status = 'Active'", (instructor['institute_id'], id))
            dept_insts = cursor.fetchall()
            db.close()
            also_apply_ids.extend([str(r['id']) for r in dept_insts])
            
        if also_apply_ids:
            unique_extra_ids = list(set([i for i in also_apply_ids if str(i) != str(id)]))
            if unique_extra_ids:
                bulk_save_proctor_availability(unique_extra_ids, entries, mode='replace')
                flash(f"Availability saved for {instructor['name']} and {len(unique_extra_ids)} other instructor(s).", "success")
            else:
                flash(f"Availability saved for {instructor['name']}.", "success")
        else:
            flash(f"Availability saved for {instructor['name']}.", "success")
            
        return redirect(url_for('faculty_page'))

    saved_dates = get_proctor_availability_for(id)
    period_start, period_end = get_exam_period()
    exam_start = period_start.strftime('%Y-%m-%d') if period_start else ''
    exam_end   = period_end.strftime('%Y-%m-%d') if period_end else ''
    
    all_instructors = get_all_instructors()
    same_dept_instructors = [
        ins for ins in all_instructors 
        if ins['id'] != id and ins.get('institute_id') == instructor.get('institute_id') and ins.get('status') == 'Active'
    ]
    
    return render_template("admin_availability.html", 
                           instructor=instructor, 
                           saved_dates=saved_dates,
                           exam_start=exam_start,
                           exam_end=exam_end,
                           same_dept_instructors=same_dept_instructors,
                           all_instructors=[ins for ins in all_instructors if ins['id'] != id and ins.get('status') == 'Active'])

@app.route("/admin/bulk_proctor_availability", methods=["POST"])
def admin_bulk_proctor_availability():
    guard = require_role('admin')
    if guard: return guard
    
    instructor_ids = request.form.getlist("instructor_ids")
    if not instructor_ids:
        raw_ids = request.form.get("instructor_ids_csv", "")
        if raw_ids:
            instructor_ids = [i.strip() for i in raw_ids.split(",") if i.strip()]
            
    if not instructor_ids:
        flash("No instructors selected for availability update.", "warning")
        return redirect(url_for('faculty_page'))
        
    dates       = request.form.getlist("available_dates")
    start_times = request.form.getlist("start_times")
    end_times   = request.form.getlist("end_times")
    mode        = request.form.get("availability_mode", "replace") # 'replace' or 'append'
    
    entries = []
    for i, d in enumerate(dates):
        d_str = str(d).strip()
        if not d_str: continue
        st = start_times[i].strip() if i < len(start_times) and start_times[i].strip() else '07:00'
        et = end_times[i].strip() if i < len(end_times) and end_times[i].strip() else '20:00'
        entries.append({'date': d_str, 'start_time': st, 'end_time': et})
        
    bulk_save_proctor_availability(instructor_ids, entries, mode=mode)
    action_desc = "appended to" if mode == "append" else "set for"
    flash(f"Availability successfully {action_desc} {len(instructor_ids)} selected instructor(s).", "success")
    return redirect(url_for('faculty_page'))

# â”€â”€ IMPORT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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

# â”€â”€ EXPORT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    prepared_by = session.get('full_name', 'Administrator')
    pdf_bytes = _pdf(sorted_groups, conflict_ids, exam_term=exam_term, exam_semester=exam_semester, prepared_by=prepared_by)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='exam_schedule.pdf')

@app.route("/export/absence_report.pdf")
def export_absence_pdf():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    from system.exporter import export_proctor_report_pdf
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    absence   = get_proctor_absence_report(date_from or None, date_to or None)
    hours     = get_all_proctor_hours_summary()
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    prepared_by = session.get('full_name', 'Administrator')
    pdf_bytes = export_proctor_report_pdf(hours, absence, exam_term=exam_term, exam_semester=exam_semester, prepared_by=prepared_by, report_type='absence')
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='proctor_absence_report.pdf')

@app.route("/export/assignment_report.pdf")
def export_assignment_pdf():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    from system.exporter import export_proctor_report_pdf
    hours   = get_all_proctor_hours_summary()
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    prepared_by = session.get('full_name', 'Administrator')
    pdf_bytes = export_proctor_report_pdf(hours, [], exam_term=exam_term, exam_semester=exam_semester, prepared_by=prepared_by, report_type='assignment')
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='proctor_assignment_report.pdf')

@app.route("/export/collection_report.pdf")
def export_collection_pdf():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    from system.exporter import export_collection_report_pdf
    data = get_exam_collection_status()
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    prepared_by = session.get('full_name', 'Administrator')
    pdf_bytes = export_collection_report_pdf(data, exam_term=exam_term, exam_semester=exam_semester, prepared_by=prepared_by)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='collection_report.pdf')

# ── REPORTS ─────────────────────────────────────────────────────────────────

@app.route("/reports/clear_absence", methods=["POST"])
def clear_absence_reports_route():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    clear_absence_reports()
    flash("Proctor absence reports cleared.", "success")
    return redirect(url_for('reports_page'))

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

    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    prepared_by = session.get('full_name', 'Administrator')
    prepared_by_role = session.get('role', 'admin').capitalize()
    from datetime import datetime
    generated_at = datetime.now().strftime("%B %d, %Y %I:%M %p")

    return render_template("reports.html",
                           absence_report=absence,
                           assignment_report=assignment,
                           scheduling_report=scheduling,
                           date_from=date_from, date_to=date_to,
                           exam_term=exam_term,
                           exam_semester=exam_semester,
                           prepared_by=prepared_by,
                           prepared_by_role=prepared_by_role,
                           generated_at=generated_at,
                           unread_count=unread)

# ── EXAM ARCHIVES (HISTORICAL RECORDS) ──────────────────────────────────────

@app.route("/admin/archives")
def admin_archives():
    guard = require_role('admin', 'secretary')
    if guard: return guard
    archives = get_exam_archives()
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    unread = _get_unread(session['user_id'])
    return render_template("archives.html",
                           archives=archives,
                           current_term=exam_term,
                           current_semester=exam_semester,
                           unread_count=unread)

@app.route("/admin/archives/create", methods=["POST"])
def admin_archives_create():
    guard = require_role('admin')
    if guard: return guard
    academic_year = request.form.get("academic_year", "2025-2026").strip()
    exam_term = request.form.get("exam_term", "Midterm").strip()
    exam_semester = request.form.get("exam_semester", "1st Semester").strip()
    archive_title = request.form.get("archive_title", "").strip()
    notes = request.form.get("notes", "").strip()

    ok, res = create_exam_archive(
        academic_year=academic_year,
        exam_term=exam_term,
        exam_semester=exam_semester,
        archive_title=archive_title or None,
        notes=notes or None,
        user_id=session.get('user_id'),
        user_name=session.get('full_name')
    )
    if ok:
        flash(f"Successfully created historical archive '{archive_title or f'A.Y. {academic_year} {exam_semester} {exam_term}'}'.", "success")
    else:
        flash(f"Failed to create archive: {res}", "danger")
    return redirect(url_for('admin_archives'))

@app.route("/admin/archives/<int:archive_id>")
def admin_archive_view(archive_id):
    guard = require_role('admin', 'secretary')
    if guard: return guard
    archive = get_exam_archive_by_id(archive_id)
    if not archive:
        flash("Archived record not found.", "danger")
        return redirect(url_for('admin_archives'))
    unread = _get_unread(session['user_id'])
    settings = get_system_settings() or {}
    return render_template("archive_view.html",
                           archive=archive,
                           settings=settings,
                           unread_count=unread)

@app.route("/admin/archives/<int:archive_id>/sync_durations", methods=["POST"])
def admin_archive_sync_durations(archive_id):
    guard = require_role('admin')
    if guard: return guard
    ok, msg = sync_archive_durations(archive_id)
    if ok:
        flash("Archive durations and end times successfully synchronized with current settings.", "success")
    else:
        flash(f"Failed to sync archive durations: {msg}", "danger")
    return redirect(url_for('admin_archive_view', archive_id=archive_id))

@app.route("/admin/archives/<int:archive_id>/export_csv")
def admin_archive_export_csv(archive_id):
    guard = require_role('admin', 'secretary')
    if guard: return guard
    archive = get_exam_archive_by_id(archive_id)
    if not archive:
        flash("Archived record not found.", "danger")
        return redirect(url_for('admin_archives'))

    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject Name", "Subject Code", "Section", "Subject Type",
        "Exam Date", "Start Time", "End Time", "Duration (min)",
        "Room", "Building", "Floor", "Proctor", "Institute"
    ])
    for ex in archive.get('exams', []):
        writer.writerow([
            ex.get('subject_name', ''),
            ex.get('subject_code', ''),
            ex.get('section', ''),
            ex.get('subject_type', ''),
            ex.get('formatted_date') or (ex.get('exam_date_time')[:10] if ex.get('exam_date_time') else ''),
            ex.get('formatted_time', ''),
            ex.get('formatted_time_end', ''),
            ex.get('duration_minutes', 60),
            ex.get('room_name', ''),
            ex.get('building', ''),
            ex.get('floor', ''),
            ex.get('instructor_name', ''),
            ex.get('institute_name', '')
        ])

    csv_data = output.getvalue()
    safe_title = "".join(c for c in archive.get('archive_title', 'archive') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"{safe_title}.csv"
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response

@app.route("/admin/archives/<int:archive_id>/export_pdf")
def admin_archive_export_pdf(archive_id):
    guard = require_role('admin', 'secretary')
    if guard: return guard
    archive = get_exam_archive_by_id(archive_id)
    if not archive:
        flash("Archived record not found.", "danger")
        return redirect(url_for('admin_archives'))

    from system.exporter import export_archive_pdf
    pdf_bytes = export_archive_pdf(archive)
    safe_title = "".join(c for c in archive.get('archive_title', 'archive') if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"{safe_title}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route("/admin/archives/<int:archive_id>/delete", methods=["POST"])
def admin_archive_delete(archive_id):
    guard = require_role('admin')
    if guard: return guard
    ok, msg = delete_exam_archive(archive_id)
    if ok:
        flash(msg, "success")
    else:
        flash(f"Error deleting archive: {msg}", "danger")
    return redirect(url_for('admin_archives'))

# â”€â”€ SETTINGS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    
    cur_settings = get_system_settings() or {}

    def get_int(key, default):
        val = request.form.get(key, "").strip()
        if val:
            try: return int(val)
            except ValueError: pass
        return int(cur_settings.get(key, default) or default)

    def get_float(key, default):
        val = request.form.get(key, "").strip()
        if val:
            try: return float(val)
            except ValueError: pass
        return float(cur_settings.get(key, default) or default)

    save_system_settings(
        day_start=request.form.get("day_start") or cur_settings.get("day_start", "07:00"),
        day_end=request.form.get("day_end") or cur_settings.get("day_end", "20:00"),
        slot_interval_min=get_int("slot_interval_min", 60),
        max_proctor_hrs=get_int("max_consecutive_proctor_hrs", 3),
        travel_buffer_min=get_int("travel_buffer_min", 15),
        smtp_host=request.form.get("smtp_host", cur_settings.get("smtp_host", "")),
        smtp_port=get_int("smtp_port", 587),
        smtp_user=request.form.get("smtp_user", cur_settings.get("smtp_user", "")),
        smtp_password=request.form.get("smtp_password", cur_settings.get("smtp_password", "")),
        smtp_from=request.form.get("smtp_from", cur_settings.get("smtp_from", "")),
        smtp_use_tls=1 if request.form.get("smtp_use_tls") else cur_settings.get("smtp_use_tls", 0),
        major_duration_hrs=get_float("major_duration_hrs", 2.0),
        minor_duration_hrs=get_float("minor_duration_hrs", 1.0),
        max_daily_proctor_hrs=get_float("max_daily_proctor_hrs", 4.0)
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
            
    # Automatically synchronize all historical archives with the new duration settings
    try:
        sync_archive_durations()
    except Exception as e:
        print("Auto-sync archives error:", e)

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
            subject="CCA Exam Management â€” Test Email",
            recipients=[to],
            body="This is a test email from the CCA Exam Management System. SMTP is configured correctly."
        )
        mail.send(msg)
        flash(f"Test email sent to {to}.", "success")
    except Exception as e:
        flash(f"Failed to send email: {e}", "danger")
    return redirect(url_for('settings_page'))

# â”€â”€ CHANGE PASSWORD (Admin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            flash(f" Password changed for {user['full_name']}.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for(redirect_to))

def derive_user_reset_password(full_name=None):
    """
    Generates a secure, cryptographically random temporary password for administrative reset.
    Complies with NIST SP 800-63B guidelines (high entropy, non-predictable).
    Format: CCA-XXXX-XXXX (e.g., CCA-8F2B-4A19)
    """
    import secrets
    token = secrets.token_hex(4).upper()
    return f"CCA-{token[:4]}-{token[4:]}"

@app.route("/admin/reset_password/<int:user_id>", methods=["POST"])
def admin_reset_password(user_id):
    guard = require_role('admin')
    if guard: return guard
    redirect_to = request.form.get("redirect_to", "students_page")
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            c = db.cursor(dictionary=True)
            c.execute("SELECT full_name, role FROM users WHERE id = %s", (user_id,))
            user = c.fetchone()
            if not user or user['role'] not in ('student', 'proctor'):
                flash("User not found or not allowed.", "danger")
                return redirect(url_for(redirect_to))
            
            # Reset to custom password or generate cryptographically random temporary password
            default_pw = request.form.get("new_password", "").strip() or derive_user_reset_password(user['full_name'])
            hashed = _bcrypt.hashpw(default_pw.encode(), _bcrypt.gensalt()).decode()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            db.commit()
            log_audit_event('USER_PASSWORD_RESET', f"Admin reset password for user ID {user_id} ({user['full_name']})", user_id=session.get('user_id'), user_name=session.get('full_name'), user_role=session.get('role'), ip_address=request.remote_addr)
            flash(f"Password for {user['full_name']} has been reset to temporary password: '{default_pw}'. Please provide this to the user.", "success")
        except Exception as e:
            flash(f"Error resetting password: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for(redirect_to))


# â”€â”€ STUDENTS (Admin-accessible) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/students")
def students_page():
    guard = require_role('admin')
    if guard: return guard
    pending_students = get_pending_users()
    all_students     = get_all_students()
    institutes       = get_all_institutes()
    unread           = _get_unread(session['user_id'])
    pending_count    = len(pending_students)
    
    db_conn = open_db()
    sections = []
    if db_conn:
        try:
            cur = db_conn.cursor()
            cur.execute("SELECT DISTINCT section FROM (SELECT section FROM users WHERE section IS NOT NULL AND section != '' UNION SELECT section FROM exams WHERE section IS NOT NULL AND section != '') AS s ORDER BY section")
            sections = [r[0] for r in cur.fetchall()]
        finally:
            db_conn.close()

    return render_template("students.html",
                           pending_students=pending_students,
                           all_students=all_students,
                           institutes=institutes,
                           unread_count=unread,
                           pending_count=pending_count,
                           sections=sections)

@app.route("/admin/edit_student/<int:user_id>", methods=["POST"])
def admin_edit_student(user_id):
    guard = require_role('admin')
    if guard: return guard
    new_section = request.form.get("section", "").strip()
    new_name = request.form.get("full_name", "").strip()
    new_email = request.form.get("email", "").strip()
    redirect_to = request.form.get("redirect_to", "students_page")
    
    db = open_db()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, full_name FROM users WHERE id = %s AND role = 'student'", (user_id,))
            student = cursor.fetchone()
            if not student:
                flash("Student not found.", "danger")
                return redirect(url_for(redirect_to))
            
            cursor.execute("""
                UPDATE users 
                SET section = %s,
                    full_name = CASE WHEN %s != '' THEN %s ELSE full_name END,
                    email = CASE WHEN %s != '' THEN %s ELSE email END
                WHERE id = %s AND role = 'student'
            """, (new_section, new_name, new_name, new_email, new_email, user_id))
            db.commit()
            flash(f"Student '{student['full_name']}' updated successfully. Section is now '{new_section or 'None'}'.", "success")
        except Exception as e:
            flash(f"Error updating student: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for(redirect_to))

@app.route("/students/approve/<int:id>", methods=["POST"])
def admin_approve_student(id):
    guard = require_role('admin')
    if guard: return guard
    approve_student(id)
    flash(" Student account approved. They have been notified.", "success")
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
    flash(" Student account reactivated.", "success")
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
        flash(f" {len(user_ids)} student(s) deactivated.", "warning")
    elif action == 'delete':
        bulk_delete_students(user_ids)
        flash(f" {len(user_ids)} student(s) deleted.", "danger")
    elif action == 'approve':
        for uid in user_ids:
            approve_student(uid)
        flash(f" {len(user_ids)} student(s) approved.", "success")
    elif action == 'reset_password':
        import bcrypt as _bcrypt
        db = open_db()
        if db:
            try:
                c = db.cursor(dictionary=True)
                format_strings = ','.join(['%s'] * len(user_ids))
                c.execute(f"SELECT id, full_name FROM users WHERE id IN ({format_strings}) AND role='student'", user_ids)
                students = c.fetchall()
                for st in students:
                    pw = derive_user_reset_password(st['full_name'])
                    hashed = _bcrypt.hashpw(pw.encode(), _bcrypt.gensalt()).decode()
                    c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, st['id']))
                db.commit()
                flash(f"Secure randomized temporary passwords generated for {len(students)} student(s).", "success")
            except Exception as e:
                flash(f"Error resetting passwords: {e}", "danger")
            finally:
                db.close()
    else:
        flash("Unknown action.", "danger")
    return redirect(url_for('students_page'))

# â”€â”€ SUPER ADMIN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/super_admin")
def super_admin_page():
    guard = require_super_admin()
    if guard: return guard
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
    guard = require_super_admin()
    if guard: return guard
    approve_student(id)
    flash("Student account approved and notified.", "success")
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/reject_student/<int:id>", methods=["POST"])
def reject_student_route(id):
    guard = require_super_admin()
    if guard: return guard
    err = delete_user(id)
    if err:
        flash(f"Could not reject: {err}", "danger")
    else:
        flash("Student registration rejected and removed.", "success")
    return redirect(url_for('super_admin_page'))

@app.route("/super_admin/edit_user/<int:id>", methods=["POST"])
def super_edit_user(id):
    guard = require_super_admin()
    if guard: return guard
    try:
        # Construct full name from 4 fields if they exist, otherwise fallback to "name"
        last = request.form.get("last_name", "").strip()
        first = request.form.get("first_name", "").strip()
        middle = request.form.get("middle_name", "").strip()
        suffix = request.form.get("suffix", "").strip()
        
        if last and first:
            # Format: Lastname, Firstname M. Suffix
            full_name = f"{last}, {first}"
            if middle:
                full_name += f" {middle[0]}." if len(middle) == 1 else f" {middle}"
            if suffix:
                full_name += f" {suffix}"
        else:
            full_name = request.form.get("name", "").strip()
            
        email        = request.form.get("email", "").strip()
        role         = request.form.get("role", "student").strip()
        section      = request.form.get("section", "").strip()
        institute_id = request.form.get("institute_id") or None
        is_sa        = 1 if request.form.get("is_super_admin") else 0

        # Validate role
        if role not in ("admin", "secretary", "proctor", "student"):
            flash("Invalid role selected.", "danger")
            return redirect(url_for('super_admin_page'))

        # GET OLD EMAIL FIRST before updating DB!
        from system.database import open_db, update_user
        db = open_db()
        old_email = None
        if db:
            try:
                c = db.cursor(dictionary=True)
                c.execute("SELECT email FROM users WHERE id = %s", (id,))
                row = c.fetchone()
                if row: old_email = row['email']
            finally:
                db.close()

        # Update local DB
        update_user(id, full_name, email, role, section, institute_id, is_sa)
        flash(f"User '{full_name}' updated successfully to role '{role}'.", "success")
    except Exception as e:
        flash(f"Error updating user: {str(e)}", "danger")
    return redirect(url_for('super_admin_page'))


@app.route("/super_admin/update_email", methods=["POST"])
def super_update_email():
    guard = require_super_admin()
    if guard: return guard
    
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
                
            # Get current email to verify user exists
            c.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            current_user = c.fetchone()
            
            if current_user:
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
    guard = require_super_admin()
    if guard: return guard
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
    guard = require_super_admin()
    if guard: return guard
    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            c = db.cursor(dictionary=True)
            c.execute("SELECT id, full_name, email, role FROM users WHERE id = %s", (id,))
            target_user = c.fetchone()
            if not target_user:
                flash("User not found.", "danger")
                return redirect(url_for('super_admin_page'))
            
            custom_pw = request.form.get("new_password", "").strip()
            if custom_pw:
                default_pw = custom_pw
            else:
                default_pw = derive_user_reset_password(target_user.get('full_name') or 'User')
            
            hashed = _bcrypt.hashpw(default_pw.encode(), _bcrypt.gensalt()).decode()
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, id))
            db.commit()
            flash(f"Password for {target_user['full_name']} reset to default ({default_pw}) successfully.", "success")
        except Exception as e:
            flash(f"Error resetting password: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))

# â”€â”€ PROCTOR DASHBOARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/proctor")
def proctor_dashboard():
    guard = require_role('proctor')
    if guard: return guard
    is_pub = is_schedule_published()
    instructor_id = session.get('instructor_id')
    if not is_pub:
        exams = []
        total_hours = 0.0
        sorted_groups = []
    else:
        exams = get_proctor_exams(instructor_id) if instructor_id else []
        total_hours = get_proctor_total_hours(instructor_id) if instructor_id else 0.0
        grouped = defaultdict(list)
        for exam in exams:
            dt = exam['exam_date_time']
            if not dt: continue
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            dur = int(exam.get('duration_minutes') or 60)
            end_dt = dt + timedelta(minutes=dur)
            exam['time'] = dt.strftime("%I:%M %p")
            exam['time_end'] = end_dt.strftime("%I:%M %p")
            exam['time_range'] = f"{exam['time']} - {exam['time_end']}"
            grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
        sorted_groups = sorted(grouped.items(),
                               key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    saved_dates = get_proctor_availability_for(instructor_id) if instructor_id else []
    period_start, period_end = get_exam_period()
    period_dates = []
    if period_start and period_end:
        cur = period_start
        while cur <= period_end:
            period_dates.append(str(cur))
            cur += timedelta(days=1)
    unread = _get_unread(session['user_id'])
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    full_name = session.get('full_name', 'Faculty Proctor')
    prepared_by = session.get('full_name', 'Faculty Proctor')
    return render_template("proctor_dashboard.html",
                           grouped=sorted_groups,
                           exams=exams,
                           total=len(exams),
                           full_name=full_name,
                           exam_term=exam_term,
                           exam_semester=exam_semester,
                           saved_dates=saved_dates,
                           period_dates=period_dates,
                           period_start=str(period_start) if period_start else '',
                           period_end=str(period_end) if period_end else '',
                           total_hours=total_hours,
                           unread_count=unread,
                           prepared_by=prepared_by,
                           is_published=is_pub)

@app.route("/proctor/schedule.pdf")
def export_proctor_schedule_pdf_route():
    guard = require_role('proctor')
    if guard: return guard
    instructor_id = session.get('instructor_id')
    if not instructor_id:
        flash("Instructor profile not linked to account.", "danger")
        return redirect(url_for('proctor_dashboard'))
    
    exams = get_proctor_exams(instructor_id)
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    total_hours = get_proctor_total_hours(instructor_id)
    
    from system.exporter import export_proctor_duty_slip_pdf
    pdf_bytes = export_proctor_duty_slip_pdf(
        proctor_name=session.get('full_name', 'Faculty Proctor'),
        exams=exams,
        exam_term=exam_term,
        exam_semester=exam_semester,
        total_hours=total_hours,
        prepared_by=session.get('full_name', 'Faculty Proctor')
    )
    
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', session.get('full_name', 'proctor')).strip('_').lower()
    filename = f"proctor_schedule_{safe_name}.pdf" if safe_name else "proctor_schedule.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )



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
    
    # Prevent duplicate absence submissions for the same exam
    db = open_db()
    if db:
        try:
            c = db.cursor(dictionary=True)
            c.execute("""
                SELECT pa.id, (SELECT COUNT(*) FROM relievers rel WHERE rel.exam_id = %s) as has_reliever
                FROM proctor_absence pa
                WHERE pa.instructor_id = %s AND pa.exam_id = %s
                ORDER BY pa.id DESC LIMIT 1
            """, (exam_id, instructor_id, exam_id))
            prev = c.fetchone()
            if prev:
                if prev.get('has_reliever'):
                    flash("A substitute reliever has already been assigned for this exam.", "info")
                    return redirect(url_for('proctor_dashboard'))
                else:
                    flash("An absence report is already pending administrative / secretary review for this exam.", "warning")
                    return redirect(url_for('proctor_dashboard'))
        finally:
            db.close()

    record_proctor_absence(instructor_id, int(exam_id), reason, session['user_id'])
    flash("Absence reported successfully. Your Institute Secretary has been notified.", "info")
    exam = get_exam_by_id(int(exam_id)) if exam_id else {}
    exam_label = f"{exam.get('subject_name', '')} ({exam.get('section', '')})" if exam else f"exam #{exam_id}"
    # Notify admin and secretary roles
    title = f"Proctor Absence: {session.get('full_name', 'Proctor')}"
    msg   = f"{session.get('full_name', 'Proctor')} reported an absence for {exam_label}. Reason: {reason or 'Not specified'}."
    create_notification_for_role('admin', title, msg)
    create_notification_for_role('secretary', title, msg)
    return redirect(url_for('proctor_dashboard'))

# â”€â”€ RELIEVERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
                        "CCA â€” You have been assigned as a Reliever",
                        f"Dear {row['full_name']},\n\nYou have been assigned as a reliever proctor for exam #{exam_id}.\n"
                        f"Reason: {reason or 'Not specified'}\n\nPlease log in for details.\n\nCCA Exam Management System")
            finally:
                db.close()
    else:
        flash("Select both exam and instructor.", "warning")
    return redirect(url_for('faculty_page'))

@app.route("/relievers/remove/<int:id>", methods=["POST"])
def remove_reliever_route(id):
    guard = require_role('admin')
    if guard: return guard
    remove_reliever(id)
    flash("Reliever removed.", "success")
    return redirect(url_for('faculty_page'))

# â”€â”€ SECRETARY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/secretary")
def secretary_dashboard():
    guard = require_role('secretary', 'admin')
    if guard: return guard
    is_pub = is_schedule_published()
    # Admins see all institutes; secretaries see only their own
    inst_id     = None if session.get('role') == 'admin' else session.get('institute_id')
    instructors = get_active_instructors()
    unread      = _get_unread(session['user_id'])
    
    if not is_pub and session.get('role') != 'admin':
        exams = []
        stats = {'total': 0, 'collected': 0, 'returned': 0, 'pending_collection': 0}
        pending_absences = []
    else:
        exams       = get_exam_collection_status(institute_id=inst_id)
        for ex in exams:
            dt = ex.get('exam_date_time')
            if dt:
                if isinstance(dt, str):
                    try:
                        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass
                dur = int(ex.get('duration_minutes') or 60)
                if isinstance(dt, datetime):
                    end_dt = dt + timedelta(minutes=dur)
                    ex['time'] = dt.strftime("%I:%M %p")
                    ex['time_end'] = end_dt.strftime("%I:%M %p")
                    ex['time_range'] = f"{ex['time']} - {ex['time_end']}"
        stats       = get_collection_stats(institute_id=inst_id)
        from system.database import get_unresolved_absences
        pending_absences = get_unresolved_absences(institute_id=inst_id)
    
    return render_template("secretary.html",
                           exams=exams, instructors=instructors,
                           stats=stats, unread_count=unread,
                           institute_id=inst_id,
                           pending_absences=pending_absences,
                           is_published=is_pub)

@app.route("/api/substitute_candidates/<int:exam_id>", methods=["GET"])
def api_substitute_candidates(exam_id):
    guard = require_role('secretary', 'admin')
    if guard: return jsonify({'error': 'Not authorised'}), 403
    inst_id = None if session.get('role') == 'admin' else session.get('institute_id')
    from system.database import get_substitute_candidates
    data = get_substitute_candidates(exam_id, institute_id=inst_id)
    if not data: return jsonify({'error': 'Exam not found'}), 404
    return jsonify(data)

@app.route("/secretary/assign_substitute", methods=["POST"])
def secretary_assign_substitute():
    guard = require_role('secretary', 'admin')
    if guard: return guard
    exam_id = request.form.get("exam_id")
    new_inst_id = request.form.get("instructor_id")
    new_room_id = request.form.get("room_id")
    reason = request.form.get("reason", "").strip()

    if not exam_id or not new_inst_id:
        flash("Please select an exam and substitute proctor.", "warning")
        return redirect(url_for('secretary_dashboard'))

    from system.database import reassign_exam_proctor_room
    ok, msg = reassign_exam_proctor_room(int(exam_id), int(new_inst_id), new_room_id=new_room_id, reason=reason, reassigned_by=session.get('user_id'))
    if ok:
        flash(msg, "success")
    else:
        flash(f"Failed to assign substitute: {msg}", "danger")
    return redirect(url_for('secretary_dashboard'))


@app.route("/secretary/collect/<int:exam_id>", methods=["POST"])
def secretary_collect(exam_id):
    guard = require_role('secretary', 'admin')
    if guard: return guard
    instructor_id = request.form.get("collected_by_instructor_id") or None
    notes         = request.form.get("notes", "")
    mark_exam_collected(exam_id, instructor_id, notes)
    flash("Marked as collected.", "success")
    return redirect(url_for('secretary_dashboard'))

@app.route("/secretary/batch_collect", methods=["POST"])
def secretary_batch_collect():
    guard = require_role('secretary', 'admin')
    if guard: return guard
    raw_exam_ids = request.form.getlist("exam_ids")
    if not raw_exam_ids:
        comma_ids = request.form.get("exam_ids", "")
        if comma_ids:
            raw_exam_ids = [x.strip() for x in comma_ids.split(",") if x.strip()]
    
    instructor_id = request.form.get("collected_by_instructor_id") or None
    notes         = request.form.get("notes", "")

    collected_count = 0
    for eid_str in raw_exam_ids:
        try:
            eid = int(eid_str)
            mark_exam_collected(eid, instructor_id, notes)
            collected_count += 1
        except (ValueError, TypeError):
            continue

    if collected_count > 0:
        flash(f"Successfully marked {collected_count} exam envelope(s) as collected.", "success")
    else:
        flash("No valid exams were selected for collection.", "warning")
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
    is_valid, err_msg = validate_password_strength(new_password)
    if not is_valid:
        flash(err_msg, "danger")
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
            flash(" Password changed successfully.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('secretary_dashboard'))

# â”€â”€ PROCTOR ABSENCE (Admin view) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
        
        ins = get_instructor_by_id(int(instructor_id)) if instructor_id else {}
        ins_name = ins.get('name', 'Instructor') if ins else 'Instructor'
        exam = get_exam_by_id(int(exam_id)) if exam_id else {}
        exam_label = f"{exam.get('subject_name', '')} ({exam.get('section', '')})" if exam else f"exam #{exam_id}"
        
        title = f"Proctor Absence: {ins_name}"
        msg = f"{ins_name} was reported absent for {exam_label}. Reason: {reason or 'Not specified'}."
        create_notification_for_role('admin', title, msg)
        create_notification_for_role('secretary', title, msg)
    else:
        flash("Select instructor and exam.", "warning")
    return redirect(url_for('reports_page'))

# â”€â”€ NOTIFICATIONS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/notifications/clear_all", methods=["POST"])
def clear_all_notifications_route():
    guard = require_login()
    if guard: return guard
    clear_all_notifications(session['user_id'])
    flash("All notifications cleared.", "success")
    return redirect(url_for('notifications_page'))

@app.route("/notifications")
def notifications_page():
    guard = require_login()
    if guard: return guard
    notifs = get_notifications(session['user_id'])
    unread = _get_unread(session['user_id'])
    pending_count = 0
    if session.get('role') in ['admin', 'super_admin']:
        try:
            pending_count = len(get_pending_users())
        except Exception:
            pending_count = 0
    return render_template("notifications.html",
                           notifications=notifs, unread_count=unread,
                           pending_count=pending_count)

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

# â”€â”€ CHANGE OWN PASSWORD (Proctor / Student) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/change_my_password", methods=["POST"])
def change_my_password():
    guard = require_login()
    if guard: return guard
    role = session.get('role')
    redirect_to = request.form.get("redirect_to", "")
    safe_redirects = {
        'proctor': 'proctor_dashboard',
        'student': 'student_timetable',
        'admin': 'dashboard',
        'super_admin': 'super_admin_page',
        'secretary': 'secretary_dashboard',
    }
    fallback = safe_redirects.get(role, 'login')

    def get_redirect():
        ref = request.referrer
        if ref and (request.host in ref):
            return redirect(ref)
        target = redirect_to if redirect_to in safe_redirects.values() else fallback
        return redirect(url_for(target))

    current_password = request.form.get("current_password", "").strip()
    new_password     = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "danger")
        return get_redirect()
    is_valid, err_msg = validate_password_strength(new_password)
    if not is_valid:
        flash(err_msg, "danger")
        return get_redirect()
    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return get_redirect()
    if new_password == current_password:
        flash("New password cannot be the same as your current password.", "warning")
        return get_redirect()

    db = open_db()
    if db:
        try:
            import bcrypt as _bcrypt
            c_db = db.cursor(dictionary=True)
            c_db.execute("SELECT id, password FROM users WHERE id = %s", (session['user_id'],))
            user = c_db.fetchone()
            if not user:
                flash("User account not found.", "danger")
                return get_redirect()

            stored_pw = user.get('password') or ''
            try:
                current_ok = _bcrypt.checkpw(current_password.encode(), stored_pw.encode())
            except (ValueError, TypeError):
                current_ok = (current_password == stored_pw)

            if not current_ok:
                flash("Current password is incorrect.", "danger")
                return get_redirect()

            hashed = _bcrypt.hashpw(new_password.encode(), _bcrypt.gensalt()).decode()
            c_db.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, session['user_id']))
            db.commit()
            flash("Password updated successfully.", "success")
        except Exception as e:
            flash(f"Error updating password: {e}", "danger")
        finally:
            db.close()
    return get_redirect()


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
            
    dates_set = set()
    times_set = set()
    sec_exams_by_start = defaultdict(lambda: defaultdict(list))
    
    for sec, exams in sections_dict.items():
        for exam in exams:
            dt = exam['exam_date_time']
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            d_str = dt.strftime("%Y-%m-%d")
            t_str = dt.strftime("%H:%M")
            exam['_date_label'] = dt.strftime("%a %b %d")
            exam['datetime_raw'] = dt.strftime("%Y-%m-%dT%H:%M")
            dur = int(exam.get('duration_minutes') or 60)
            end_dt = dt + timedelta(minutes=dur)
            exam['duration_minutes'] = dur
            exam['time'] = dt.strftime("%I:%M %p")
            exam['time_end'] = end_dt.strftime("%I:%M %p")
            exam['time_range'] = f"{exam['time']} - {exam['time_end']}"
            
            sec_exams_by_start[sec][(t_str, d_str)].append(exam)
            dates_set.add(d_str)
            times_set.add(t_str)
            
            # For multi-hour exams, ensure each hourly slot is in times_set
            extra_hours = int((dur - 1) // 60)
            for h in range(1, extra_hours + 1):
                cont_dt = dt + timedelta(hours=h)
                times_set.add(cont_dt.strftime("%H:%M"))
        
    dates_list = sorted(list(dates_set))
    times_list = sorted(list(times_set))
    
    date_labels = {}
    time_labels = {}
    for sec, exams in sections_dict.items():
        for e in exams:
            if '_date_label' in e:
                dt = e['exam_date_time']
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                date_labels[dt.strftime("%Y-%m-%d")] = e['_date_label']
                if 'time' in e:
                    time_labels[dt.strftime("%H:%M")] = e['time']

    for t_str in times_list:
        try:
            start_obj = datetime.strptime(t_str, "%H:%M")
            end_obj = start_obj + timedelta(hours=1)
            time_start_str = start_obj.strftime("%I:%M %p")
            time_end_str = end_obj.strftime("%I:%M %p")
            time_labels[t_str] = f"{time_start_str} - {time_end_str}"
        except Exception:
            time_labels[t_str] = t_str

    # Build merged-cell table rows with rowspan for each section
    section_tables = {}
    for sec, exams_map in sec_exams_by_start.items():
        active_spans = {d: 0 for d in dates_list}
        rows = []
        for t_idx, t in enumerate(times_list):
            try:
                start_obj = datetime.strptime(t, "%H:%M")
                end_obj = start_obj + timedelta(hours=1)
                t_start = start_obj.strftime("%I:%M %p")
                t_end = end_obj.strftime("%I:%M %p")
            except Exception:
                t_start = t
                t_end = ""
            row_cells = []
            for d in dates_list:
                if active_spans[d] > 0:
                    row_cells.append({'is_skipped': True, 'date': d})
                    active_spans[d] -= 1
                else:
                    cell_exams = exams_map.get((t, d), [])
                    if cell_exams:
                        max_dur = max(int(e.get('duration_minutes') or 60) for e in cell_exams)
                        start_dt = datetime.strptime(t, "%H:%M")
                        end_dt = start_dt + timedelta(minutes=max_dur)
                        span = 0
                        for check_t in times_list[t_idx:]:
                            c_dt = datetime.strptime(check_t, "%H:%M")
                            if c_dt < end_dt:
                                span += 1
                            else:
                                break
                        span = max(span, 1)
                        if span > 1:
                            active_spans[d] = span - 1
                        row_cells.append({
                            'is_skipped': False,
                            'rowspan': span,
                            'exams': cell_exams,
                            'date': d
                        })
                    else:
                        row_cells.append({
                            'is_skipped': False,
                            'rowspan': 1,
                            'exams': [],
                            'date': d
                        })
            rows.append({
                'time_str': t,
                'time_start': t_start,
                'time_end': t_end,
                'time_label': time_labels.get(t, t),
                'cells': row_cells
            })
        section_tables[sec] = rows
                
    return render_template("batch_print.html",
                           time_labels=time_labels,
                           section_tables=section_tables,
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
    is_pub = is_schedule_published()
    section      = session.get('section', '')
    institute_id = session.get('institute_id')
    full_name    = session.get('full_name', 'Student')
    if not is_pub:
        exams = []
        sorted_groups = []
    else:
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
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    unread = _get_unread(session['user_id'])
    
    db_conn = open_db()
    available_sections = []
    if db_conn:
        try:
            cur = db_conn.cursor()
            cur.execute("SELECT DISTINCT section FROM (SELECT section FROM users WHERE section IS NOT NULL AND section != '' UNION SELECT section FROM exams WHERE section IS NOT NULL AND section != '') AS s ORDER BY section")
            available_sections = [r[0] for r in cur.fetchall()]
        finally:
            db_conn.close()

    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name=full_name,
                           institute_name=institute_name,
                           exam_term=exam_term,
                           exam_semester=exam_semester,
                           unread_count=unread,
                           is_published=is_pub,
                           available_sections=available_sections)

@app.route("/student/schedule.pdf")
def export_student_schedule_pdf_route():
    guard = require_role('student')
    if guard: return guard
    section      = session.get('section', '')
    institute_id = session.get('institute_id')
    full_name    = session.get('full_name', 'Student')
    exams = get_public_timetable(section=section, institute_id=institute_id)
    term_tuple = get_exam_term()
    exam_term = term_tuple[0] if term_tuple and term_tuple[0] else 'Midterm'
    exam_semester = term_tuple[1] if term_tuple and len(term_tuple) > 1 and term_tuple[1] else '1st Semester'
    
    from system.exporter import export_student_permit_pdf
    pdf_bytes = export_student_permit_pdf(
        student_name=full_name,
        section=section,
        exams=exams,
        exam_term=exam_term,
        exam_semester=exam_semester
    )
    
    import re
    safe_sec = re.sub(r'[^a-zA-Z0-9]+', '_', section).strip('_').lower() if section else 'student'
    filename = f"exam_permit_{safe_sec}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )

@app.route("/student/update_section", methods=["POST"])
def student_update_section():
    guard = require_role('student')
    if guard: return guard
    new_section = request.form.get("section", "").strip()
    if not new_section:
        flash("Please select a valid section.", "error")
        return redirect(url_for('student_timetable'))
    
    db = open_db()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("UPDATE users SET section = %s WHERE id = %s", (new_section, session['user_id']))
            db.commit()
            session['section'] = new_section
            flash(f"Section successfully updated to '{new_section}'. Timetable refreshed.", "success")
        except Exception as e:
            flash(f"Error updating section: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('student_timetable'))

# â”€â”€ MISC â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.route("/clear-session")
def clear_session():
    session.clear()
    response = redirect(url_for('index'))
    response.delete_cookie('session')
    return response

# â”€â”€ RUN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9999))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(debug=True, host=host, port=port)









