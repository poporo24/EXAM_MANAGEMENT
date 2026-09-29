import sys

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update generate_schedule to save exam_semester
gen_find = '''    period_end_str   = request.form.get("period_end")
    exam_term = request.form.get("exam_term", "Midterm")
    session['exam_term'] = exam_term'''
gen_repl = '''    period_end_str   = request.form.get("period_end")
    exam_term = request.form.get("exam_term", "Midterm")
    exam_semester = request.form.get("exam_semester", "1st Semester")
    session['exam_term'] = exam_term
    session['exam_semester'] = exam_semester'''
content = content.replace(gen_find, gen_repl)

# 2. Update schedule_view to pass exam_semester
sv_find = '''                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
sv_repl = '''                           exam_term=session.get('exam_term', 'Midterm/Final'),
                           exam_semester=session.get('exam_semester', '1st Semester'))'''
content = content.replace(sv_find, sv_repl)

# 3. Update student_timetable to pass exam_semester
st_find = '''                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
st_repl = '''                           exam_term=session.get('exam_term', 'Midterm/Final'),
                           exam_semester=session.get('exam_semester', '1st Semester'))'''
content = content.replace(st_find, st_repl)

# 4. Update admin_batch_print_sections to pass exam_semester
abp_find = '''                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
abp_repl = '''                           exam_term=session.get('exam_term', 'Midterm/Final'),
                           exam_semester=session.get('exam_semester', '1st Semester'))'''
content = content.replace(abp_find, abp_repl)

# 5. Update admin_print_section to pass exam_semester
aps_find = '''                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
aps_repl = '''                           exam_term=session.get('exam_term', 'Midterm/Final'),
                           exam_semester=session.get('exam_semester', '1st Semester'))'''
content = content.replace(aps_find, aps_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
