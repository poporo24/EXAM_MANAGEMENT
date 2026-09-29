import sys

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('<p>School Year: 2025-2026</p>', '<p>{{ exam_semester }}, School Year: 2025-2026</p>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

replace_in_file('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html')
replace_in_file('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html')
replace_in_file('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\batch_print.html')

# Add Semester Dropdown to schedule.html Generate form
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

form_find = '''                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Exam Term</label>'''
form_repl = '''                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Semester</label>
                            <select name="exam_semester" required class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none">
                                <option value="1st Semester">1st Semester</option>
                                <option value="2nd Semester">2nd Semester</option>
                                <option value="Summer">Summer</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Exam Term</label>'''

content = content.replace(form_find, form_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)

