with open("app.py", "r", encoding="utf-8") as f:
    app_py = f.read()

import re

old_route = """@app.route("/edit_exam_schedule/<int:exam_id>", methods=["POST"])
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
    ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str)"""

new_route = """@app.route("/edit_exam_schedule/<int:exam_id>", methods=["POST"])
def edit_exam_schedule(exam_id):
    guard = require_role('admin')
    if guard: return guard
    new_room_id  = int(request.form.get('room_id', 0))
    new_inst_id  = int(request.form.get('instructor_id', 0))
    new_dt_str   = request.form.get('exam_datetime', '')
    duration     = int(float(request.form.get('duration_hours', 1)) * 60)
    force        = request.form.get('force_save') == '1'
    sync_all     = request.form.get('sync_all_sections') == 'on'
    
    if not force:
        conflicts = check_edit_conflicts(exam_id, new_room_id, new_inst_id, new_dt_str, duration)
        if conflicts:
            flash('Edit blocked: ' + ' | '.join(conflicts), 'danger')
            return redirect(url_for('schedule_view'))
    ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str, sync_all=sync_all)"""

if old_route in app_py:
    app_py = app_py.replace(old_route, new_route)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_py)
    print("Patched edit route for sync_all")
else:
    print("Could not find old route")
