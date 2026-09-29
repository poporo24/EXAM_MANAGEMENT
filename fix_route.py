import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_string = '''@app.route("/login", methods=["GET", "POST"])

@app.route("/public/timetable")'''

content = content.replace(bad_string, '@app.route("/public/timetable")')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
