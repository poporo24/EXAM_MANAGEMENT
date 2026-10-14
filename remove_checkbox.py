with open('template/register.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '<div class="flex items-start pt-2">' in line and 'terms' in lines[i+2]:
        skip = True
    if skip and '</div>' in line and 'class="pt-2"' in lines[i+2]:
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open('template/register.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
