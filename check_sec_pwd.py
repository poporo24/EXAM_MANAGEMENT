app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def secretary_change_password' in line:
        print("".join(lines[i:i+40]))
        break
