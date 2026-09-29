import os
import re

filepath = os.path.join('system', 'database.py')
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

insert = '''
def save_exam_term(exam_term, exam_semester):
    db = open_db()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE exam_settings SET exam_term = %s, exam_semester = %s WHERE id = 1", (exam_term, exam_semester))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO exam_settings (id, exam_term, exam_semester) VALUES (1, %s, %s)", (exam_term, exam_semester))
        db.commit()
    finally:
        db.close()

def get_exam_term():
    db = open_db()
    if not db: return ("Midterm", "1st Semester")
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT exam_term, exam_semester FROM exam_settings WHERE id = 1")
        row = cursor.fetchone()
        if row:
            term = row.get('exam_term')
            sem = row.get('exam_semester')
            return (term if term else "Midterm", sem if sem else "1st Semester")
        return ("Midterm", "1st Semester")
    finally:
        db.close()
'''

# Find the end of get_exam_period
pattern = re.compile(r'def get_exam_period\(\):.*?\n    finally:\n        db\.close\(\)\n', re.DOTALL)
match = pattern.search(content)

if match:
    end_idx = match.end()
    new_content = content[:end_idx] + "\n" + insert + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected exam_term functions")
else:
    print("Could not find get_exam_period")
