import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

route = '''
@app.route("/admin/print_section")
def admin_print_section():
    guard = require_role('admin')
    if guard: return guard
    section = request.args.get('section', '').strip()
    if not section:
        flash("Please select a section.", "error")
        return redirect(url_for('schedule_view'))
    
    exams = get_public_timetable(section=section)
    from collections import defaultdict
    grouped = defaultdict(list)
    for exam in exams:
        dt = exam['exam_date_time']
        if not dt: continue
        if isinstance(dt, str):
            from datetime import datetime
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        exam['time']     = dt.strftime("%I:%M %p")
        from datetime import timedelta
        exam['time_end'] = (dt + timedelta(minutes=int(exam['duration_minutes'] or 60))).strftime("%I:%M %p")
        grouped[dt.strftime("%A, %B %d, %Y")].append(exam)
    
    sorted_groups = sorted(grouped.items(), key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name="Admin Generated",
                           institute_name="City College of Angeles")
'''

content = content.replace('@app.route("/timetable")', route + '\n@app.route("/timetable")')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
