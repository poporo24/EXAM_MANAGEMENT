import re

html_path = 'template/reports.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_include = "{% include 'admin_sidebar.html' %}"
new_include = '''{% if session.get('role') == 'secretary' %}
        {% include 'secretary_sidebar.html' %}
    {% else %}
        {% include 'admin_sidebar.html' %}
    {% endif %}'''

if old_include in html:
    html = html.replace(old_include, new_include)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed reports.html sidebar logic")
else:
    print("Could not find admin_sidebar.html include in reports.html")
