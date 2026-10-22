with open('system/database.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = "VALUES (%s, %s, %s, %s, \\'Pending\\', %s, %s)\"\"\",\n                    (row.get('subject_name'), row.get('section') or None,\n                     subject_type, dur_min,\n                     row.get('institute_id')))"

replacement = "VALUES (%s, %s, %s, %s, \\'Pending\\', %s, %s)\"\"\",\n                    (row.get('subject_name'), row.get('section') or None,\n                     subject_type, dur_min,\n                     row.get('institute_id'), row.get('subject_id')))"

if target in text:
    text = text.replace(target, replacement)
    with open('system/database.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully patched system/database.py for exam import")
else:
    print("Target not found")
