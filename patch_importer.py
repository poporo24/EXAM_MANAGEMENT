import re

# 1. Update system/importer.py
with open("system/importer.py", "r", encoding="utf-8") as f:
    imp = f.read()

imp = imp.replace("subject_name = row.get('subject_name', '').strip()", "subject_code = row.get('subject_code', '').strip()")
imp = imp.replace("if not subject_name:", "if not subject_code:")
imp = imp.replace("errors.append(f\"Row {i+2}: Missing subject_name\")", "errors.append(f\"Row {i+2}: Missing subject_code\")")
imp = imp.replace("'subject_name': subject_name,", "'subject_code': subject_code,")
imp = imp.replace("Expected columns: subject_name, section", "Expected columns: subject_code, section")

with open("system/importer.py", "w", encoding="utf-8") as f:
    f.write(imp)

# 2. Update system/database.py bulk_import_exams
with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

old_insert = """                cursor.execute(
                    \"\"\"INSERT INTO exams (subject_name, section, subject_type, duration_minutes, status, institute_id)
                       VALUES (%s, %s, %s, %s, 'Pending', %s)\"\"\",
                    (row.get('subject_name'), row.get('section'), dur_min, row.get('institute_id')))"""
                    
# Wait, let's just use regex because indentation could differ.
db = re.sub(
    r'INSERT INTO exams \(subject_name, section, subject_type, duration_minutes, status, institute_id\)\s+VALUES \(%s, %s, %s, %s, \'Pending\', %s\)',
    r'INSERT INTO exams (subject_name, section, subject_type, duration_minutes, status, institute_id, subject_id)\n                       VALUES (%s, %s, %s, %s, \'Pending\', %s, %s)',
    db
)

db = re.sub(
    r'\(row\.get\(\'subject_name\'\), row\.get\(\'section\'\), subject_type, dur_min, row\.get\(\'institute_id\'\)\)',
    r"(row.get('subject_name'), row.get('section'), subject_type, dur_min, row.get('institute_id'), row.get('subject_id'))",
    db
)

with open("system/database.py", "w", encoding="utf-8") as f:
    f.write(db)

# 3. Update app.py import_exams
with open("app.py", "r", encoding="utf-8") as f:
    app_c = f.read()

old_app = """    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    for r in rows:
        code = r.pop('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
    ok, errors = bulk_import_exams(rows)"""

new_app = """    institutes = {i['code']: i['id'] for i in get_all_institutes()}
    subjects_by_code = {s['code'].upper(): s for s in get_all_subjects()}
    
    for r in rows:
        code = r.pop('institute_code', '').upper()
        r['institute_id'] = institutes.get(code)
        
        subj_code = r.pop('subject_code', '').upper()
        subj = subjects_by_code.get(subj_code)
        if subj:
            r['subject_id'] = subj['id']
            r['subject_name'] = subj['name']
        else:
            r['subject_id'] = None
            r['subject_name'] = subj_code # Fallback to code if not found

    ok, errors = bulk_import_exams(rows)"""

app_c = app_c.replace(old_app, new_app)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_c)

print("Backend patched")
