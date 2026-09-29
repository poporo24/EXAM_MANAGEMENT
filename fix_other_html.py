import sys

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('<p>Midterm/Final term examination test</p>', '<p>{{ exam_term }} Examination</p>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

replace_in_file('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html')
replace_in_file('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\batch_print.html')

