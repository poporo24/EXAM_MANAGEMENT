with open("template/secretary.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace exam.id with exam.exam_id
html = html.replace('exam.id', 'exam.exam_id')

with open("template/secretary.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Replaced exam.id with exam.exam_id")
