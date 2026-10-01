import re

with open("app.py", "r", encoding="utf-8") as f:
    app = f.read()

new_func = r"""@app.route("/faculty/<int:id>/edit", methods=["POST"])
def faculty_edit(id):
    guard = require_role('admin')
    if guard: return guard
    
    last = request.form.get("last_name", "").strip()
    first = request.form.get("first_name", "").strip()
    middle = request.form.get("middle_name", "").strip()
    suffix = request.form.get("suffix", "").strip()
    
    if last and first:
        full_name = f"{last}, {first}"
        if middle:
            full_name += f" {middle[0]}." if len(middle) == 1 else f" {middle}"
        if suffix:
            full_name += f" {suffix}"
    else:
        full_name = request.form.get("name", "").strip()
        
    edit_instructor(id,
        full_name,
        request.form.get("institute_id") or None,
        request.form.get("building", ""),
        1 if request.form.get("is_pwd") else 0,
        request.form.get("subjects_taught", "")
    )
    flash("Instructor updated.", "success")
    return redirect(url_for('faculty_page'))"""

app = re.sub(r'@app\.route\("/faculty/<int:id>/edit", methods=\["POST"\]\).*?return redirect\(url_for\(\'faculty_page\'\)\)', new_func, app, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app)
print("Patched faculty_edit")
