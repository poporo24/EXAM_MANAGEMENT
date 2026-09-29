import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded term in print header
content = content.replace('<p>Midterm/Final term examination test</p>', '<p>{{ exam_term }} Examination</p>')

# Add Exam Term dropdown to generate form
form_find = '''                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Filter Institute</label>'''
form_repl = '''                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Exam Term</label>
                            <select name="exam_term" required class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none">
                                <option value="Midterm">Midterm</option>
                                <option value="Finals">Finals</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Filter Institute</label>'''
content = content.replace(form_find, form_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
