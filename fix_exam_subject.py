import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

exam_find = '''@app.route("/add_exam", methods=["POST"])
def create_exam():
    guard = require_role('admin')
    if guard: return guard
    subject_id = request.form.get("subject_id")
    section = request.form.get("section", "").strip()
    
    existing_exams = get_all_exams()
    if any(str(e.get('subject_id')) == str(subject_id) and e.get('section', '').lower() == section.lower() for e in existing_exams):
        flash(f"Warning: An exam for this subject and section already exists.", "error")
        return redirect(url_for('dashboard') + '#exams')

    add_exam(
        request.form.get("name"),'''

exam_repl = '''@app.route("/add_exam", methods=["POST"])
def create_exam():
    guard = require_role('admin')
    if guard: return guard
    subject_id = request.form.get("subject_id")
    section = request.form.get("section", "").strip()
    
    existing_exams = get_all_exams()
    if any(str(e.get('subject_id')) == str(subject_id) and e.get('section', '').lower() == section.lower() for e in existing_exams):
        flash(f"Warning: An exam for this subject and section already exists.", "error")
        return redirect(url_for('dashboard') + '#exams')

    # Auto-fetch subject name to ensure it exactly matches the linked subject
    existing_subjects = get_all_subjects()
    subject_name = next((s['name'] for s in existing_subjects if str(s['id']) == str(subject_id)), request.form.get("name", "Unknown"))

    add_exam(
        subject_name,'''

content = content.replace(exam_find, exam_repl)
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
