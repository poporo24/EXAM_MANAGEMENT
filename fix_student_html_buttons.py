import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('{% if full_name != "Admin Generated" %}', '{% if full_name not in ["Admin Generated", "Irregular Student Viewer"] %}')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'w', encoding='utf-8') as f:
    f.write(content)
