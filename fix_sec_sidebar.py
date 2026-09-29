import re

path = 'template/secretary_sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace dashboard link
html = html.replace(
    '<a href="/secretary" class="flex items-center px-4 py-3 bg-green-50 text-[#668054] border-r-4 border-[#668054] group" title="Exam Collection">',
    '<a href="/secretary" class="flex items-center px-4 py-3 group {% if active_page == \'dashboard\' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Exam Collection">'
)

# Replace reports link
html = html.replace(
    '<a href="/reports" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 hover:text-[#668054] group" title="Reports">',
    '<a href="/reports" class="flex items-center px-4 py-3 group {% if active_page == \'reports\' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Reports">'
)

# Replace notifications link
html = html.replace(
    '<a href="/notifications" class="flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 hover:text-[#668054] group" title="Notifications">',
    '<a href="/notifications" class="flex items-center px-4 py-3 group {% if active_page == \'notifications\' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Notifications">'
)

# Fix the profile section (it probably says "Admin User")
html = html.replace('Admin User', 'Secretary')
html = html.replace('Administrator', 'College Secretary')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
