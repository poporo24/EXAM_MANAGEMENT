import re

html_path = 'template/secretary.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Extract the sidebar block
match = re.search(r'(<!-- Sidebar -->.*?)</aside>', html, flags=re.DOTALL)
if match:
    sidebar_content = match.group(1) + '</aside>'
    with open('template/secretary_sidebar.html', 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
    
    # Replace the sidebar in secretary.html with the include
    new_html = html.replace(sidebar_content, "{% set active_page = 'dashboard' %}\n    {% include 'secretary_sidebar.html' %}")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Extracted secretary_sidebar.html")
else:
    print("Could not find sidebar in secretary.html")
