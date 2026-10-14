import re

with open("template/admin_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()

pattern = r'<a href="/notifications".*?</a>'
html = re.sub(pattern, '', html, flags=re.DOTALL)

with open("template/admin_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Removed notifications from admin_sidebar.html!")
