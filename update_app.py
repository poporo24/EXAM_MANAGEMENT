import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# I will replace the extraction of full_name with the 4 fields
old_line = 'full_name    = request.form.get("full_name", "").strip()'
new_lines = '''
    first_name   = request.form.get("first_name", "").strip()
    last_name    = request.form.get("last_name", "").strip()
    middle_name  = request.form.get("middle_name", "").strip()
    suffix       = request.form.get("suffix", "").strip()
    
    # Format the name: "Lastname, Firstname M. Suffix"
    middle_initial = (middle_name[0].upper() + ".") if middle_name else ""
    full_name_parts = [part for part in [first_name, middle_initial, suffix] if part]
    formatted_first_part = " ".join(full_name_parts)
    full_name = f"{last_name}, {formatted_first_part}" if last_name and formatted_first_part else (last_name or formatted_first_part)
'''

if old_line in app_content:
    app_content = app_content.replace(old_line, new_lines.strip('\n'))
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("Updated app.py")
else:
    print("Could not find full_name extraction in app.py!")
