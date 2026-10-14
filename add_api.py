import re
with open("app.py", "r", encoding="utf-8") as f:
    app_py = f.read()

new_api = """@app.route("/api/suggest_times", methods=["POST"])
def api_suggest_times():
    guard = require_role('admin')
    if guard: return jsonify([])
    data = request.get_json(force=True)
    exam_id = int(data.get('exam_id', 0))
    duration = int(data.get('duration_minutes', 60))
    room_id = int(data.get('room_id', 0))
    proctor_id = int(data.get('instructor_id', 0))
    
    from system.database import get_suggested_times
    suggestions = get_suggested_times(exam_id, duration, room_id, proctor_id)
    return jsonify({'suggestions': suggestions})

@app.route("/api/available_resources","""

if "/api/suggest_times" not in app_py:
    app_py = app_py.replace('@app.route("/api/available_resources",', new_api)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_py)
    print("Added /api/suggest_times endpoint")
else:
    print("Already exists")
