import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('    from collections import defaultdict\n', '')
content = content.replace('            from datetime import datetime\n', '')
content = content.replace('        from datetime import timedelta\n', '')
content = content.replace('    from datetime import datetime\n', '')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
