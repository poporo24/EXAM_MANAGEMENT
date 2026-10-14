with open("system/importer.py", "r", encoding="utf-8") as f:
    code = f.read()

import re

old_func = """def parse_instructors_csv(file_content_bytes):
    \"\"\"Expected columns: name, institute_code, building, subjects_taught
    Returns list of dicts.\"\"\"
    rows = []
    errors = []
    try:
        content = file_content_bytes.decode('utf-8-sig').strip()
        if not content: return ([], ["Empty file"])
        reader = csv.DictReader(io.StringIO(content))
        for i, row in enumerate(reader):
            try:
                name = row.get('name', '').strip()
                if not name:
                    errors.append(f"Row {i+2}: Missing name")
                    continue
                rows.append({
                    'name': name,
                    'email': row.get('email', '').strip(),
                    'institute_code': row.get('institute_code', '').strip(),
                    'building': row.get('building', '').strip(),
                    'is_pwd': int(row.get('is_pwd', 0) or 0),
                    'subjects_taught': row.get('subjects_taught', '').strip()
                })
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
    except Exception as e:
        errors.append(f"File Error: {str(e)}")
    return (rows, errors)"""

new_func = """def parse_instructors_csv(file_content_bytes):
    \"\"\"Expected columns: name, institute_code, building, subjects_taught, availability
    Returns list of dicts.\"\"\"
    import re
    rows = []
    errors = []
    try:
        content = file_content_bytes.decode('utf-8-sig').strip()
        if not content: return ([], ["Empty file"])
        reader = csv.DictReader(io.StringIO(content))
        for i, row in enumerate(reader):
            try:
                name = row.get('name', '').strip()
                if not name:
                    errors.append(f"Row {i+2}: Missing name")
                    continue
                    
                # Parse availability string e.g. "Mon 07:00-12:00, Wed"
                raw_avail = row.get('availability', '').strip()
                parsed_avail = []
                if raw_avail:
                    parts = [p.strip() for p in raw_avail.split(',')]
                    for p in parts:
                        match = re.match(r'^([A-Za-z]+)\s*(?:(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2}))?$', p)
                        if match:
                            day = match.group(1)[:3].capitalize() # Mon, Tue, Wed
                            start = match.group(2) or '07:00'
                            end = match.group(3) or '20:00'
                            parsed_avail.append({'day': day, 'start': start, 'end': end})
                        else:
                            errors.append(f"Row {i+2}: Invalid availability format '{p}'")
                
                rows.append({
                    'name': name,
                    'email': row.get('email', '').strip(),
                    'institute_code': row.get('institute_code', '').strip(),
                    'building': row.get('building', '').strip(),
                    'is_pwd': int(row.get('is_pwd', 0) or 0),
                    'subjects_taught': row.get('subjects_taught', '').strip(),
                    'availability': parsed_avail
                })
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
    except Exception as e:
        errors.append(f"File Error: {str(e)}")
    return (rows, errors)"""

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("system/importer.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched importer successfully!")
else:
    print("Could not find old_func!")
