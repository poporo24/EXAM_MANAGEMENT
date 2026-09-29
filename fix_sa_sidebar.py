html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix aside tag
html = html.replace(
    '<aside id="sidebar" class="bg-white border-r border-gray-200 fixed h-full w-64 sidebar-transition z-20 flex flex-col">',
    '<aside id="sidebar" class="bg-white border-r border-gray-200 fixed h-screen w-64 sidebar-transition z-20 flex flex-col overflow-hidden">'
)

# Fix nav tag
html = html.replace(
    '<nav class="flex-1 overflow-y-auto py-4 space-y-1">',
    '<nav class="flex-1 overflow-y-auto py-4 space-y-1 min-h-0">'
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed super_admin.html sidebar scrolling!")
