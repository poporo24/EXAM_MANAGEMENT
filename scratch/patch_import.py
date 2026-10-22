with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Subjects import
text = text.replace(
    "institutes = {i['code']: i['id'] for i in get_all_institutes()}",
    "institutes = {i['code'].upper(): i['id'] for i in get_all_institutes() if i and i.get('code')}"
)

# 2. Exams import
text = text.replace(
    "subjects_by_code = {s['code'].upper(): s for s in get_all_subjects()}",
    "subjects_by_code = {s['code'].upper(): s for s in get_all_subjects() if s and s.get('code')}"
)

text = text.replace(
    "subj_code = r.pop('subject_code', '').upper()",
    "subj_code = (r.pop('subject_code', '') or '').upper()"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated app.py successfully')
