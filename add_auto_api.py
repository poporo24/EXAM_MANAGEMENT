import re
with open("app.py", "r", encoding="utf-8") as f:
    app_py = f.read()

new_api = """@app.route("/api/auto_schedule_exam", methods=["POST"])
def api_auto_schedule_exam():
    guard = require_role('admin')
    if guard: return jsonify({})
    data = request.get_json(force=True)
    exam_id = int(data.get('exam_id', 0))
    duration = int(data.get('duration_minutes', 60))
    
    from system.database import get_full_auto_schedule
    result = get_full_auto_schedule(exam_id, duration)
    return jsonify(result or {})

@app.route("/api/suggest_times","""

if "/api/auto_schedule_exam" not in app_py:
    app_py = app_py.replace('@app.route("/api/suggest_times",', new_api)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_py)
    print("Added /api/auto_schedule_exam endpoint")
else:
    print("Already exists")
