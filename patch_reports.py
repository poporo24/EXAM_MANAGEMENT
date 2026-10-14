with open("template/reports.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('{{ rep.exam_date }}', '{{ rep.exam_date_time }}')
html = html.replace('{{ rep.created_at }}', '{{ rep.reported_at }}')

with open("template/reports.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched reports.html!")
