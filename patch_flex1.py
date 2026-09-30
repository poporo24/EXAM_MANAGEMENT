with open("template/admin_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace('class="flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text"', 
                    'class="flex-1 flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text"')
with open("template/admin_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("template/secretary_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace('class="flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text"', 
                    'class="flex-1 flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text"')
with open("template/secretary_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Added flex-1")
