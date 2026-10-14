import re

with open('app.py', 'r', encoding='utf-8') as f:
    data = f.read()

old_code = r'''    period_start_str = request\.form\.get\("period_start"\)
    period_end_str   = request\.form\.get\("period_end"\)
    exam_term = request\.form\.get\("exam_term", "Midterm"\)
    exam_semester = request\.form\.get\("exam_semester", "1st Semester"\)
    save_exam_term\(exam_term, exam_semester\)
    try:
        period_start = date\.fromisoformat\(period_start_str\)
        period_end   = date\.fromisoformat\(period_end_str\)
    except \(TypeError, ValueError\):
        flash\("Please select a valid exam period\.", "warning"\)
        return redirect\(url_for\('schedule_view'\)\)

    if period_end < period_start:
        flash\("End date must be after start date\.", "warning"\)
        return redirect\(url_for\('schedule_view'\)\)

    save_exam_period\(period_start, period_end\)'''

new_code = '''    period_start_str = request.form.get("period_start")
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
            major_duration_hrs=settings.get('major_duration_hrs', 2.0),
            minor_duration_hrs=settings.get('minor_duration_hrs', 1.0)
        )
        settings = get_system_settings() # reload'''

data = re.sub(old_code, new_code, data)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(data)
