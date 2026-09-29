import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

old_query = 'SELECT DISTINCT section FROM users WHERE section IS NOT NULL AND section != '' ORDER BY section'
new_query = 'SELECT DISTINCT section FROM (SELECT section FROM users WHERE section IS NOT NULL AND section != '' UNION SELECT section FROM exams WHERE section IS NOT NULL AND section != '') AS all_sections ORDER BY section'

# Need to escape the quotes for the Python string replacement, or just replace the specific string
# Let's use a robust replace
old_line = 'cursor.execute("SELECT DISTINCT section FROM users WHERE section IS NOT NULL AND section != \'\' ORDER BY section")'
new_line = 'cursor.execute("SELECT DISTINCT section FROM (SELECT section FROM users WHERE section IS NOT NULL AND section != \'\' UNION SELECT section FROM exams WHERE section IS NOT NULL AND section != \'\') AS all_sections ORDER BY section")'

if old_line in app_content:
    app_content = app_content.replace(old_line, new_line)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("Fixed section query to include exams table!")
else:
    print("Could not find the exact query string.")
