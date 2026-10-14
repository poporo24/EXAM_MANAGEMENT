import re

with open('system/scheduler.py', 'r', encoding='utf-8') as f:
    data = f.read()

old_code = r'''                        scheduled.append\(\{
                            'exam_id': e\['id'\],
                            'room_id': r\['id'\],
                            'instructor_id': i\['id'\],
                            'instructor_name': i\['name'\],
                            'exam_date_time': start_dt,
                        \}\)'''

new_code = '''                        scheduled.append({
                            'exam_id': e['id'],
                            'subject_name': e.get('subject_name', 'Unknown Subject'),
                            'section': e.get('section', ''),
                            'room_id': r['id'],
                            'instructor_id': i['id'],
                            'instructor_name': i['name'],
                            'exam_date_time': start_dt,
                        })'''

data = re.sub(old_code, new_code, data)

with open('system/scheduler.py', 'w', encoding='utf-8') as f:
    f.write(data)
