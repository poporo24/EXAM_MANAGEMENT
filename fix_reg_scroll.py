import re

html_path = 'template/register.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace body classes
html = html.replace('flex items-center justify-center relative overflow-hidden', 'relative overflow-y-auto flex flex-col')

# Replace inner div classes
html = html.replace('z-10 w-full max-w-md bg-white rounded-xl shadow-xl p-8 border border-gray-100', 'z-10 w-full max-w-md bg-white rounded-xl shadow-xl p-8 border border-gray-100 m-auto')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed register.html scrolling!")
