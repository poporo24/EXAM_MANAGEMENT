import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

inst_find = '''@app.route("/institutes/add", methods=["POST"])
def add_institute_route():
    guard = require_role('admin')
    if guard: return guard
    err = add_institute(
        request.form.get("name"),'''
inst_repl = '''@app.route("/institutes/add", methods=["POST"])
def add_institute_route():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").upper().strip()
    
    existing = get_all_institutes()
    if any(i['name'].lower() == name.lower() or i['code'].upper() == code for i in existing):
        flash(f"Warning: Institute name '{name}' or code '{code}' already exists.", "error")
        return redirect(url_for('institutes_page'))

    err = add_institute(
        name,'''
content = content.replace(inst_find, inst_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
