import sys

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\system\\scheduler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
in_loop = False
for line in lines:
    if 'group_sections = [e.get' in line:
        in_loop = True
    if in_loop:
        if 'if not placed_group:' in line:
            in_loop = False
        else:
            if line.strip(): # skip empty
                line = '    ' + line
    out.append(line)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\system\\scheduler.py', 'w', encoding='utf-8') as f:
    f.writelines(out)
