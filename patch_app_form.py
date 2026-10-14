with open("app.py", "r", encoding="utf-8") as f:
    app_py = f.read()

old_apply = """    result = apply_exam_edit(
        exam_id,
        int(room_id),
        int(instructor_id),
        dt_str,
        int(float(duration_hours)*60),
        force
    )"""

new_apply = """    sync_all = request.form.get("sync_all_sections") == "1"
    result = apply_exam_edit(
        exam_id,
        int(room_id),
        int(instructor_id),
        dt_str,
        int(float(duration_hours)*60),
        force,
        sync_all
    )"""

app_py = app_py.replace(old_apply, new_apply)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_py)
print("Patched app form")
