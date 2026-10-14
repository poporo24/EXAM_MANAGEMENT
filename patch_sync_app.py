with open("app.py", "r", encoding="utf-8") as f:
    app_py = f.read()

old_api = """    duration = int(data.get('duration_minutes', 60))
    
    from system.database import get_full_auto_schedule
    result = get_full_auto_schedule(exam_id, duration)"""

new_api = """    duration = int(data.get('duration_minutes', 60))
    sync_all = bool(data.get('sync_all', False))
    
    from system.database import get_full_auto_schedule
    result = get_full_auto_schedule(exam_id, duration, sync_all=sync_all)"""

app_py = app_py.replace(old_api, new_api)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_py)
print("Patched app API")
