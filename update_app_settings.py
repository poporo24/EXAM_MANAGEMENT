import re

with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

pattern = r"@app\.route\(\"/settings/save\", methods=\[\"POST\"\]\).*?def settings_save\(\):.*?flash\(\"Settings updated\.\", \"success\"\)\s*return redirect\(url_for\(\"settings_page\"\)\)"

new_func = '''@app.route("/settings/save", methods=["POST"])
def settings_save():
    guard = require_role('admin')
    if guard: return guard
    
    current = get_system_settings() or {}
    section = request.form.get("section", "")
    
    def get_int(key, default):
        if key in request.form:
            val = request.form.get(key, "").strip()
            return int(val) if val else default
        return current.get(key, default)

    def get_float(key, default):
        if key in request.form:
            val = request.form.get(key, "").strip()
            return float(val) if val else default
        return current.get(key, default)
        
    def get_str(key, default=""):
        if key in request.form:
            return request.form.get(key, "").strip()
        return current.get(key, default)

    if section == "smtp":
        smtp_use_tls = 1 if request.form.get("smtp_use_tls") else 0
    else:
        smtp_use_tls = current.get("smtp_use_tls", 1)

    save_system_settings(
        day_start=get_str("day_start", "07:00"),
        day_end=get_str("day_end", "20:00"),
        slot_interval_min=get_int("slot_interval_min", 60),
        max_proctor_hrs=get_int("max_consecutive_proctor_hrs", 3),
        travel_buffer_min=get_int("travel_buffer_min", 15),
        smtp_host=get_str("smtp_host", ""),
        smtp_port=get_int("smtp_port", 465),
        smtp_user=get_str("smtp_user", ""),
        smtp_password=get_str("smtp_password", ""),
        smtp_from=get_str("smtp_from", ""),
        smtp_use_tls=smtp_use_tls,
        major_duration_hrs=get_float("major_duration_hrs", 2.0),
        minor_duration_hrs=get_float("minor_duration_hrs", 1.0)
    )
    flash("Settings updated.", "success")
    return redirect(url_for("settings_page"))'''

app_code = re.sub(pattern, new_func, app_code, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("Replaced settings_save via regex.")
