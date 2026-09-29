import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add get_exam_term, save_exam_term to imports from system.database
content = content.replace("save_exam_period, get_exam_period,", "save_exam_period, get_exam_period, save_exam_term, get_exam_term,")
if "save_exam_term" not in content[:1000]: # In case the first replace failed
    content = content.replace("save_exam_period,", "save_exam_period, save_exam_term, get_exam_term,")

# 1. Update generate_schedule to save using db instead of session
old_gen = '''    session['exam_term'] = exam_term
    session['exam_semester'] = exam_semester'''
new_gen = '''    save_exam_term(exam_term, exam_semester)'''
content = content.replace(old_gen, new_gen)

# 2. Update schedule_view
content = content.replace("exam_term=session.get('exam_term', 'Midterm/Final'),", "exam_term=get_exam_term()[0],")
content = content.replace("exam_semester=session.get('exam_semester', '1st Semester')", "exam_semester=get_exam_term()[1]")

# 3. Update batch_print
content = content.replace("exam_term=session.get('exam_term', 'Midterm/Final'),", "exam_term=get_exam_term()[0],")
content = content.replace("exam_semester=session.get('exam_semester', '1st Semester')", "exam_semester=get_exam_term()[1]")

# 4. Update student_timetable
content = content.replace("exam_term=session.get('exam_term', 'Midterm/Final'),", "exam_term=get_exam_term()[0],")
content = content.replace("exam_semester=session.get('exam_semester', '1st Semester')", "exam_semester=get_exam_term()[1]")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py")
