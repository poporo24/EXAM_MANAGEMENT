import sys
import re

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update generate_schedule to save exam_term
gen_find = '''    period_start_str = request.form.get("period_start")
    period_end_str   = request.form.get("period_end")'''
gen_repl = '''    period_start_str = request.form.get("period_start")
    period_end_str   = request.form.get("period_end")
    exam_term = request.form.get("exam_term", "Midterm")
    session['exam_term'] = exam_term'''
content = content.replace(gen_find, gen_repl)

# 2. Update schedule_view to pass exam_term
sv_find = '''                           filter_section=filter_section)'''
sv_repl = '''                           filter_section=filter_section,
                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
content = content.replace(sv_find, sv_repl)

# 3. Update student_timetable to pass exam_term
st_find = '''                           institute_name=institute_name)'''
st_repl = '''                           institute_name=institute_name,
                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
content = content.replace(st_find, st_repl)

# 4. Update admin_batch_print_sections to pass exam_term
abp_find = '''                           date_labels=date_labels)'''
abp_repl = '''                           date_labels=date_labels,
                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
content = content.replace(abp_find, abp_repl)

# 5. Update admin_print_section to pass exam_term
aps_find = '''                           institute_name="City College of Angeles")'''
aps_repl = '''                           institute_name="City College of Angeles",
                           exam_term=session.get('exam_term', 'Midterm/Final'))'''
content = content.replace(aps_find, aps_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
