import re

html_path = 'template/admin_sidebar.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the Settings link and inject the Super Admin link right above it
settings_link = '''        <a href="/settings" class="flex items-center px-4 py-3 group {% if active_page == 'settings' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Settings">'''

super_admin_link = '''        {% if session.get('is_super_admin') %}
        <div class="px-4 py-2 mt-2 text-xs font-semibold text-gray-400 uppercase tracking-wider nav-text">Super Admin</div>
        <a href="/super_admin" class="flex items-center px-4 py-3 group {% if active_page == 'super_admin' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="User Management">
            <i class="fa-solid fa-users-cog w-6 text-center text-lg"></i>
            <span class="ml-3 nav-text font-medium">User Management</span>
        </a>
        {% endif %}
'''

if settings_link in html:
    html = html.replace(settings_link, super_admin_link + settings_link)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added User Management link to admin_sidebar.html")
else:
    print("Could not find Settings link in admin_sidebar.html")
