import sys
code = '''
def get_available_resources(exam_id, datetime_str, duration_minutes):
    from datetime import datetime as _dt, timedelta as _td
    db = open_db()
    if not db: return {'rooms': [], 'instructors': []}
    try:
        cursor = db.cursor(dictionary=True)
        try:
            new_start = _dt.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                new_start = _dt.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            except Exception:
                return {'rooms': [], 'instructors': []}
        new_end = new_start + _td(minutes=duration_minutes)

        cursor.execute("SELECT r.id, r.room_name as name, r.capacity FROM rooms r ORDER BY r.room_name")
        all_rooms = cursor.fetchall()

        cursor.execute("SELECT id, name FROM instructors WHERE status='Active' ORDER BY name")
        all_insts = cursor.fetchall()

        cursor.execute(
            "SELECT room_id, instructor_id, exam_date_time, duration_minutes FROM exams "
            "WHERE status='Scheduled' AND exam_date_time IS NOT NULL AND id!=%s",
            (exam_id,)
        )
        busy_rooms = set()
        busy_insts = set()
        for row in cursor.fetchall():
            r_start = row['exam_date_time']
            if isinstance(r_start, str):
                r_start = _dt.strptime(r_start, '%Y-%m-%d %H:%M:%S')
            r_end = r_start + _td(minutes=row['duration_minutes'] or 60)
            if new_start < r_end and r_start < new_end:
                if row['room_id']: busy_rooms.add(row['room_id'])
                if row['instructor_id']: busy_insts.add(row['instructor_id'])

        return {
            'rooms': [{'id': r['id'], 'name': f"{r['name']} (Cap: {r['capacity']})"} for r in all_rooms if r['id'] not in busy_rooms],
            'instructors': [{'id': i['id'], 'name': i['name']} for i in all_insts if i['id'] not in busy_insts]
        }
    finally:
        db.close()
'''
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\system\\database.py', 'a', encoding='utf-8') as f:
    f.write('\n' + code)
