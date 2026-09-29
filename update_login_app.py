import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update login GET to pass sections
login_find = '''    if request.method == "GET":
        if 'user_id' in session and session.get('role'):
            return _redirect_by_role()
        return render_template("login.html")'''

login_repl = '''    if request.method == "GET":
        if 'user_id' in session and session.get('role'):
            return _redirect_by_role()
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("login.html", sections=sections)'''

content = content.replace(login_find, login_repl)

# 2. Add public timetable route
public_route = '''
@app.route("/public/timetable")
def public_timetable():
    section = request.args.get('section', '').strip()
    if not section:
        flash("Please select a section.", "error")
        return redirect(url_for('login'))
    
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
    
    from datetime import datetime
    sorted_groups = sorted(grouped.items(), key=lambda x: datetime.strptime(x[0], "%A, %B %d, %Y"))
    
    return render_template("student_timetable.html",
                           grouped=sorted_groups,
                           total=len(exams),
                           section=section,
                           full_name="Irregular Student Viewer",
                           institute_name="City College of Angeles",
                           exam_term=session.get('exam_term', 'Midterm/Final'),
                           exam_semester=session.get('exam_semester', '1st Semester'))
'''

# Place it after login route
import re
content = re.sub(r'def login\(\):[\s\S]*?if user == \'inactive\':', public_route + '\n@app.route("/login", methods=["GET", "POST"])\ndef login():\n    if request.method == "GET":\n        if \'user_id\' in session and session.get(\'role\'):\n            return _redirect_by_role()\n        all_exams = get_schedule_results()\n        sections = sorted(list(set(e.get(\'section\', \'\').strip() for e in all_exams if e.get(\'section\', \'\').strip() and e.get(\'status\') == \'Scheduled\')))\n        return render_template("login.html", sections=sections)\n\n    # POST - process credentials\n    email    = request.form.get("email", "").strip()\n    password = request.form.get("password", "").strip()\n    user = verify_login(email, password)\n    if user == \'inactive\':', content, count=1)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
