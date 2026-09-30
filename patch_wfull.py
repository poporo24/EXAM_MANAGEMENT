with open("template/admin_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace('class="h-16 flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container"', 
                    'class="h-16 w-full flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container"')
with open("template/admin_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("template/secretary_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace('class="h-16 flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container"', 
                    'class="h-16 w-full flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container"')
with open("template/secretary_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Added w-full")
