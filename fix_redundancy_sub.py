import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

sub_find = '''@app.route("/subjects/add", methods=["POST"])
def add_subject_route():
    guard = require_role('admin')
    if guard: return guard
    add_subject(
        request.form.get("name"),'''
sub_repl = '''@app.route("/subjects/add", methods=["POST"])
def add_subject_route():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    
    existing = get_all_subjects()
    if any(s['code'].lower() == code.lower() for s in existing if s.get('code')):
        flash(f"Warning: Subject code '{code}' already exists.", "error")
        return redirect(url_for('subjects_page'))
        
    add_subject(
        name,'''
content = content.replace(sub_find, sub_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
