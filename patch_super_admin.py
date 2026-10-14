with open("template/super_admin.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# Replace the whole <aside>...</aside> with include
pattern = r'<aside id="sidebar".*?</aside>'
replacement = "{% include 'admin_sidebar.html' %}"

html = re.sub(pattern, replacement, html, flags=re.DOTALL)

with open("template/super_admin.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched super_admin.html!")
