import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
    date_labels = {}
    for sec, exams in sections_dict.items():
        for e in exams:
            if '_date_label' in e:
                dt = e['exam_date_time']
                if isinstance(dt, str):
                    from datetime import datetime
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                date_labels[dt.strftime("%Y-%m-%d")] = e['_date_label']
'''

import re
content = re.sub(r'    date_labels = \{\}\n    for sec, exams in sections_dict\.items\(\):\n        for e in exams:\n            if \'_date_label\' in e:\n                date_labels\[e\[\'exam_date_time\'\]\.split\(\' \'\)\[0\]\] = e\[\'_date_label\'\]', replacement, content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
