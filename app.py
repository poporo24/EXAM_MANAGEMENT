from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from datetime import date, datetime
from collections import defaultdict

from system.database import (
    get_dashboard_stats, get_upcoming_exams,
    add_room, add_instructor, add_exam,
    get_all_rooms, get_all_instructors,
    get_pending_exams, get_already_scheduled_slots,
    apply_schedule_results, reset_schedule,
    get_schedule_results,
    delete_room, delete_instructor, delete_exam,
    get_proctor_exams, get_public_timetable,
    get_proctor_availability, get_proctor_availability_for,
    save_proctor_availability,
    register_user,
    check_conflict, update_exam_schedule,
    get_exam_by_id, check_edit_conflicts, apply_exam_edit
)
from system.scheduler import run_scheduler

app = Flask(__name__, template_folder='template')
app.secret_key = "cca_exam_management_secret_key"

# ── HELPERS ────────────────────────────────────────────────────────────────────

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

# ── AUTH ───────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if 'user_id' in session:
        if not session.get('role'):
            session.clear()
            return render_template("login.html")
        return _redirect_by_role()
    return render_template("login.html")

def _redirect_by_role():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('dashboard'))
    elif role == 'proctor':
        return redirect(url_for('proctor_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_timetable'))
    session.clear()
    return redirect(url_for('index'))

@app.route("/login", methods=["POST"])
def login():
    email    = request.form.get("email")
    password = request.form.get("password")
    from system.logic import verify_login
    user = verify_login(email, password)
    if user:
        session.clear()
        session['user_id']       = user['id']
        session['full_name']     = user['full_name']
        session['role']          = user.get('role', 'student')
        session['instructor_id'] = user.get('instructor_id')
        return _redirect_by_role()
    flash("Invalid email or password.", "error")
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/clear-session")
def clear_session():
    session.clear()
    response = redirect(url_for('index'))
    response.delete_cookie('session')
    return response

# ── REGISTER ──────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET"])
def register_page():
    if 'user_id' in session:
        return _redirect_by_role()
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_submit():
    full_name = request.form.get("full_name", "").strip()
    email     = request.form.get("email", "").strip()
    password  = request.form.get("password", "").strip()
    if not full_name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('register_page'))
    result = register_user(full_name, email, password, 'student')
    if result == 'ok':
        flash("Account created! You can now log in.", "success")
        return redirect(url_for('index'))
    elif result == 'email_taken':
        flash("That email is already registered.", "danger")
        return redirect(url_for('register_page'))
    else:
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for('register_page'))

# ── ADMIN DASHBOARD ────────────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    guard = require_role('admin')
    if guard: return guard
    stats       = get_dashboard_stats()
    exams       = get_upcoming_exams()
    rooms       = get_all_rooms()
    instructors = get_all_instructors()
    return render_template("dashboard.html",
                           stats=stats, exams=exams,
                           rooms=rooms, instructors=instructors)

# ── ADD ROUTES (admin only) ────────────────────────────────────────────────────

@app.route("/add_room", methods=["POST"])
def create_room():
    guard = require_role('admin')
    if guard: return guard
    add_room(request.form.get("room_name"), request.form.get("capacity"))
    return redirect(url_for('dashboard'))

@app.route("/add_instructor", methods=["POST"])
def create_instructor():
    guard = require_role('admin')
    if guard: return guard
    add_instructor(request.form.get("name"), request.form.get("department"))
    return redirect(url_for('dashboard'))

@app.route("/add_exam", methods=["POST"])
def create_exam():
    guard = require_role('admin')
    if guard: return guard
    add_exam(
        request.form.get("name"),
        request.form.get("section", "").strip(),
        request.form.get("subject_type", "Major"),
        request.form.get("duration_minutes", 60)
    )
    return redirect(url_for('dashboard'))

# ── DELETE ROUTES (admin only) ─────────────────────────────────────────────────

@app.route("/delete_room/<int:id>")
def remove_room(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_room(id)
    if err:
        flash(f'Cannot delete room: {err}', 'danger')
    else:
        flash('Room deleted successfully.', 'success')
    return redirect(url_for('dashboard') + '#rooms')

@app.route("/delete_instructor/<int:id>")
def remove_instructor(id):
    guard = require_role('admin')
    if guard: return guard
    err = delete_instructor(id)
    if err:
        flash(f'Cannot delete instructor: {err}', 'danger')
    else:
        flash('Instructor deleted successfully.', 'success')
    return redirect(url_for('dashboard') + '#instructors')

@app.route("/delete_exam/<int:id>")
def remove_exam(id):
    guard = require_role('admin')
    if guard: return guard
    delete_exam(id)
    return redirect(url_for('dashboard'))

# ── SCHEDULE GENERATION (admin only) ──────────────────────────────────────────

@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    guard = require_role('admin')
    if guard: return guard

    # Read exam period from form
    period_start_str = request.form.get("period_start")
    period_end_str   = request.form.get("period_end")

    try:
        period_start = date.fromisoformat(period_start_str)
        period_end   = date.fromisoformat(period_end_str)
    except (TypeError, ValueError):
        flash("Please select a valid exam period (start and end date).", "warning")
        return redirect(url_for('schedule_view'))

    if period_end < period_start:
        flash("End date must be after start date.", "warning")
        return redirect(url_for('schedule_view'))

    pending     = get_pending_exams()
    rooms       = get_all_rooms()
    instructors = get_all_instructors()
    booked      = get_already_scheduled_slots()
    proctor_av  = get_proctor_availability()

    if not rooms:
        flash("⚠️ No rooms found. Add at least one room first.", "warning")
        return redirect(url_for('schedule_view'))
    if not instructors:
        flash("⚠️ No instructors found. Add at least one instructor first.", "warning")
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
        proctor_availability=proctor_av
    )

    failed_ids = [f['exam_id'] for f in result['failed']]
    apply_schedule_results(result['scheduled'], failed_ids)
    session['last_failed']          = result['failed']
    session['last_scheduled_count'] = len(result['scheduled'])
    return redirect(url_for('schedule_view'))

@app.route("/reset_schedule", methods=["POST"])
def reset_schedule_route():
    guard = require_role('admin')
    if guard: return guard
    reset_schedule()
    session.pop('last_failed', None)
    session.pop('last_scheduled_count', None)
    flash('Schedule reset. All exams are back to Pending.', 'success')
    return redirect(url_for('schedule_view'))

# ── SCHEDULE VIEW (admin only) ─────────────────────────────────────────────────

@app.route("/schedule")
def schedule_view():
    guard = require_role('admin')
    if guard: return guard
    all_exams   = get_schedule_results()
    failed      = session.pop('last_failed', [])
    sched_count = session.pop('last_scheduled_count', None)
    grouped     = defaultdict(list)
    unscheduled = []
    for exam in all_exams:
        if exam['status'] == 'Scheduled':
            dt = exam['exam_date_time']
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
        else:
            unscheduled.append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))

    # ── Detect existing conflicts to highlight in the UI ─────────────────────
    scheduled_exams = [e for e in all_exams if e['status'] == 'Scheduled']
    conflict_ids = set()
    from datetime import timedelta
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
            overlaps = dt_a < end_b and dt_b < end_a
            # Same room + overlapping time => room conflict
            if overlaps and a.get('room_id') and a['room_id'] == b.get('room_id'):
                conflict_ids.add(a['id'])
                conflict_ids.add(b['id'])
            # Same subject + different time => anti-cheat violation
            subj_a = (a.get('subject_name') or '').strip().lower()
            subj_b = (b.get('subject_name') or '').strip().lower()
            if subj_a and subj_a == subj_b and dt_a != dt_b:
                conflict_ids.add(a['id'])
                conflict_ids.add(b['id'])

    return render_template("schedule.html",
                           grouped=sorted_groups,
                           unscheduled=unscheduled,
                           failed=failed,
                           sched_count=sched_count,
                           total=len(all_exams),
                           conflict_ids=conflict_ids,
                           rooms=get_all_rooms(),
                           instructors=get_all_instructors())

# ── EDIT EXAM SCHEDULE (admin only) ───────────────────────────────────────────

@app.route("/check_edit_conflict", methods=["POST"])
def check_edit_conflict():
    """AJAX endpoint — returns JSON list of conflict strings."""
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
    """Save a manually edited exam slot (admin only)."""
    guard = require_role('admin')
    if guard: return guard
    new_room_id  = int(request.form.get('room_id', 0))
    new_inst_id  = int(request.form.get('instructor_id', 0))
    new_dt_str   = request.form.get('exam_datetime', '')
    duration     = int(request.form.get('duration_minutes', 60))
    force        = request.form.get('force_save') == '1'

    if not force:
        conflicts = check_edit_conflicts(exam_id, new_room_id, new_inst_id, new_dt_str, duration)
        if conflicts:
            flash('Edit blocked: ' + ' | '.join(conflicts), 'danger')
            return redirect(url_for('schedule_view'))

    ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str)
    if ok:
        flash('Exam schedule updated successfully.', 'success')
    else:
        flash('Failed to save changes. Check server logs.', 'danger')
    return redirect(url_for('schedule_view'))


# ── PROCTOR DASHBOARD ──────────────────────────────────────────────────────────

@app.route("/proctor")
def proctor_dashboard():
    guard = require_role('proctor')
    if guard: return guard
    instructor_id = session.get('instructor_id')
    exams = get_proctor_exams(instructor_id) if instructor_id else []
    # get saved availability
    saved_dates = get_proctor_availability_for(instructor_id) if instructor_id else []
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt:
            continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    return render_template("proctor_dashboard.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           saved_dates=saved_dates)

@app.route("/proctor/availability", methods=["POST"])
def set_proctor_availability():
    guard = require_role('proctor')
    if guard: return guard
    instructor_id = session.get('instructor_id')
    if not instructor_id:
        flash("No instructor linked to your account.", "danger")
        return redirect(url_for('proctor_dashboard'))
    dates = request.form.getlist("available_dates")
    save_proctor_availability(instructor_id, dates)
    flash(f"Availability saved for {len(dates)} day(s).", "success")
    return redirect(url_for('proctor_dashboard'))

# ── STUDENT TIMETABLE ──────────────────────────────────────────────────────────

@app.route("/timetable")
def student_timetable():
    guard = require_role('student')
    if guard: return guard
    exams = get_public_timetable()
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt:
            continue
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    sorted_groups = sorted(grouped.items(),
                           key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams))

# ── RUN ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=9999)