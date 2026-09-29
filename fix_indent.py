app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

app_content = app_content.replace('        first_name   = request.form.get("first_name", "").strip()', '    first_name   = request.form.get("first_name", "").strip()')

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)
