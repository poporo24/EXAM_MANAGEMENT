import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ADD ROOM
room_find = '''@app.route("/add_room", methods=["POST"])
def create_room():
    guard = require_role('admin')
    if guard: return guard
    add_room(
        request.form.get("room_name"),'''
room_repl = '''@app.route("/add_room", methods=["POST"])
def create_room():
    guard = require_role('admin')
    if guard: return guard
    room_name = request.form.get("room_name", "").strip()
    building = request.form.get("building", "").strip()
    
    existing_rooms = get_all_rooms()
    if any(r['room_name'].lower() == room_name.lower() and r.get('building', '').lower() == building.lower() for r in existing_rooms):
        flash(f"Warning: Room '{room_name}' already exists in that building.", "error")
        return redirect(url_for('dashboard') + '#rooms')

    add_room(
        room_name,'''
content = content.replace(room_find, room_repl)

# ADD INSTRUCTOR
inst_find = '''@app.route("/add_instructor", methods=["POST"])
def create_instructor():
    guard = require_role('admin')
    if guard: return guard
    add_instructor(
        request.form.get("name"),'''
inst_repl = '''@app.route("/add_instructor", methods=["POST"])
def create_instructor():
    guard = require_role('admin')
    if guard: return guard
    name = request.form.get("name", "").strip()
    
    existing_instructors = get_all_instructors()
    if any(i['name'].lower() == name.lower() for i in existing_instructors):
        flash(f"Warning: Instructor '{name}' is already registered in the system.", "error")
        return redirect(url_for('dashboard') + '#instructors')

    add_instructor(
        name,'''
content = content.replace(inst_find, inst_repl)

# ADD EXAM
exam_find = '''@app.route("/add_exam", methods=["POST"])
def create_exam():
    guard = require_role('admin')
    if guard: return guard
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

    add_exam(
        request.form.get("name"),'''
content = content.replace(exam_find, exam_repl)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
