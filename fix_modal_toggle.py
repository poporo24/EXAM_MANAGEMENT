import re

html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace toggleModal calls with native DOM manipulation just to be safe
html = html.replace('onclick="toggleModal(\'updateEmailModal\')"', 'onclick="document.getElementById(\'updateEmailModal\').classList.toggle(\'hidden\')"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed modal toggle logic")
