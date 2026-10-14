import csv
import io

def parse_rooms_csv(file_content_bytes):
    """Parse CSV bytes. Expected columns: room_name, capacity, building, floor, institute_code, pwd_accessible
    Returns list of dicts ready for bulk_import_rooms."""
    rows = []
    errors = []
    try:
        content = file_content_bytes.decode('utf-8-sig').strip()
        if not content: return ([], ["Empty file"])
        reader = csv.DictReader(io.StringIO(content))
        for i, row in enumerate(reader):
            try:
                room_name = row.get('room_name', '').strip()
                if not room_name:
                    errors.append(f"Row {i+2}: Missing room_name")
                    continue
                capacity = int(row.get('capacity', 0) or 0)
                rows.append({
                    'room_name': room_name,
                    'capacity': capacity,
                    'building': row.get('building', '').strip(),
                    'floor': int(row.get('floor', 1) or 1),
                    'institute_code': row.get('institute_code', '').strip(),
                    'pwd_accessible': int(row.get('pwd_accessible', 0) or 0)
                })
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
    except Exception as e:
        errors.append(f"File Error: {str(e)}")
    return (rows, errors)

def parse_instructors_csv(file_content_bytes):
    """Expected columns: name, institute_code, building, subjects_taught, availability
    Returns list of dicts."""
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
    return (rows, errors)

def parse_subjects_csv(file_content_bytes):
    """Expected columns: name, code, institute_code, is_common, content_group
    Returns list of dicts."""
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
                    'code': row.get('code', '').strip(),
                    'institute_code': row.get('institute_code', '').strip(),
                    'is_common': int(row.get('is_common', 0) or 0),
                    'content_group': row.get('content_group', '').strip()
                })
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
    except Exception as e:
        errors.append(f"File Error: {str(e)}")
    return (rows, errors)

def parse_exams_csv(file_content_bytes):
    """Expected columns: subject_name, subject_code, section, subject_type, duration_minutes, institute_code
    subject_type must be 'Major' or 'Minor' (defaults to 'Major').
    Returns list of dicts ready for bulk_import_exams."""
    rows = []
    errors = []
    try:
        content = file_content_bytes.decode('utf-8-sig').strip()
        if not content: return ([], ["Empty file"])
        reader = csv.DictReader(io.StringIO(content))
        for i, row in enumerate(reader):
            try:
                subject_code = row.get('subject_code', '').strip()
                if not subject_code:
                    errors.append(f"Row {i+2}: Missing subject_code")
                    continue
                subject_type = row.get('subject_type', 'Major').strip()
                if subject_type not in ('Major', 'Minor'):
                    subject_type = 'Major'
                duration = int(row.get('duration_minutes', 60) or 60)
                rows.append({
                    'subject_name': row.get('subject_name', '').strip(),
                    'subject_code': subject_code,
                    'section': row.get('section', '').strip().upper(),
                    'subject_type': subject_type,
                    'duration_minutes': duration,
                    'institute_code': row.get('institute_code', '').strip()
                })
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")
    except Exception as e:
        errors.append(f"File Error: {str(e)}")
    return (rows, errors)
