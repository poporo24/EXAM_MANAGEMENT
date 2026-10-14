with open("system/database.py", "r", encoding="utf-8") as f:
    code = f.read()

old_bulk = """def bulk_import_instructors(rows):
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                institute_id = None
                if 'institute_code' in row and row['institute_code']:
                    cursor.execute("SELECT id FROM institutes WHERE code=%s", (row['institute_code'],))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                add_instructor(row.get('name'), institute_id, row.get('building'), row.get('is_pwd', 0), row.get('subjects_taught', ''), provided_email=row.get('email', ''))
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
    finally:
        db.close()
    return (success_count, error_list)"""

new_bulk = """def bulk_import_instructors(rows):
    from datetime import timedelta as _td
    db = open_db()
    if not db: return (0, ["DB Error"])
    success_count = 0
    error_list = []
    
    # Get exam period for date mapping
    period_start, period_end = get_exam_period()
    day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    
    try:
        cursor = db.cursor()
        for i, row in enumerate(rows):
            try:
                institute_id = None
                if 'institute_code' in row and row['institute_code']:
                    cursor.execute("SELECT id FROM institutes WHERE code=%s", (row['institute_code'],))
                    res = cursor.fetchone()
                    if res: institute_id = res[0]
                
                # Add instructor
                inst_id = add_instructor(row.get('name'), institute_id, row.get('building'), row.get('is_pwd', 0), row.get('subjects_taught', ''), provided_email=row.get('email', ''))
                
                # Save availability if present
                if inst_id and 'availability' in row and row['availability'] and period_start and period_end:
                    avail_entries = []
                    for avail in row['availability']:
                        target_wd = day_map.get(avail['day'])
                        if target_wd is not None:
                            # Find all dates in period matching this weekday
                            curr = period_start
                            while curr <= period_end:
                                if curr.weekday() == target_wd:
                                    avail_entries.append({
                                        'date': curr.isoformat(),
                                        'start_time': avail['start'],
                                        'end_time': avail['end']
                                    })
                                curr += _td(days=1)
                    if avail_entries:
                        save_proctor_availability(inst_id, avail_entries)
                
                success_count += 1
            except Exception as e:
                error_list.append(f"Row {i+1}: {str(e)}")
    finally:
        db.close()
    return (success_count, error_list)"""

if old_bulk in code:
    code = code.replace(old_bulk, new_bulk)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched bulk_import_instructors!")
else:
    print("Could not find old_bulk")
