app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''@app.route("/settings/save", methods=["POST"])
def settings_save():
    guard = require_role('admin')
    if guard: return guard
    save_system_settings(
        day_start=request.form.get("day_start", "07:00"),
        day_end=request.form.get("day_end", "20:00"),
        slot_interval_min=int(request.form.get("slot_interval_min", 60)),
        max_proctor_hrs=int(request.form.get("max_consecutive_proctor_hrs", 3)),
        travel_buffer_min=int(request.form.get("travel_buffer_min", 15)),
        smtp_host=request.form.get("smtp_host", ""),
        smtp_port=int(request.form.get("smtp_port", 587)),
        smtp_user=request.form.get("smtp_user", ""),
        smtp_password=request.form.get("smtp_password", ""),
        smtp_from=request.form.get("smtp_from", ""),
        smtp_use_tls=1 if request.form.get("smtp_use_tls") else 0,
        major_duration_hrs=float(request.form.get("major_duration_hrs", 2.0)),
        minor_duration_hrs=float(request.form.get("minor_duration_hrs", 1.0))
    )
    # Auto-update existing exams to match the new duration defaults
    major_min = int(float(request.form.get("major_duration_hrs", 2.0)) * 60)
    minor_min = int(float(request.form.get("minor_duration_hrs", 1.0)) * 60)'''

new_code = '''@app.route("/settings/save", methods=["POST"])
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
    minor_min = int(get_float("minor_duration_hrs", 1.0) * 60)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed settings save logic!")
else:
    print("Could not find old settings logic!")
