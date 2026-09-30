with open("system/importer.py", "r", encoding="utf-8") as f:
    imp = f.read()

imp = imp.replace("Expected columns: subject_code, section", "Expected columns: subject_name, subject_code, section")

# Add subject_name parsing
old_append = """                rows.append({
                    'subject_code': subject_code,"""
new_append = """                rows.append({
                    'subject_name': row.get('subject_name', '').strip(),
                    'subject_code': subject_code,"""

if old_append in imp:
    imp = imp.replace(old_append, new_append)
else:
    print("Could not find old_append")

with open("system/importer.py", "w", encoding="utf-8") as f:
    f.write(imp)
print("importer.py patched")

with open("app.py", "r", encoding="utf-8") as f:
    app_c = f.read()

app_c = app_c.replace(
    "r['subject_name'] = subj_code # Fallback to code if not found",
    "r['subject_name'] = r.get('subject_name') or subj_code # Fallback to CSV name, or code"
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_c)
print("app.py patched")
