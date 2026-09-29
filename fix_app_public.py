import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

find_logic = '''@app.route("/public/timetable")
def public_timetable():
    section = request.args.get('section', '').strip()
    if not section:
        flash("Please select a section.", "error")
        return redirect(url_for('login'))'''

repl_logic = '''@app.route("/public/timetable")
def public_timetable():
    section = request.args.get('section', '').strip()
    if not section:
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("irregular_portal.html", sections=sections)'''

content = content.replace(find_logic, repl_logic)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
