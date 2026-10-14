with open("template/admin_sidebar.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add Notifications under Dashboard
notif = """<a href="/dashboard" class="flex items-center px-4 py-3 group {% if active_page == 'dashboard' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Dashboard">
            <i class="fa-solid fa-chart-line w-6 text-center text-lg"></i>
            <span class="ml-3 nav-text font-medium">Dashboard</span>
        </a>
        
        <a href="/notifications" class="flex items-center px-4 py-3 group {% if active_page == 'notifications' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Notifications">
            <i class="fa-solid fa-bell w-6 text-center text-lg relative">
                {% if unread_count and unread_count > 0 %}
                <span class="absolute top-0 right-0 -mt-1 -mr-1 flex h-2 w-2">
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                </span>
                {% endif %}
            </i>
            <span class="ml-3 nav-text font-medium">Notifications</span>
        </a>"""
html = html.replace("""<a href="/dashboard" class="flex items-center px-4 py-3 group {% if active_page == 'dashboard' %}bg-green-50 text-[#668054] border-r-4 border-[#668054]{% else %}text-gray-600 hover:bg-gray-50 hover:text-[#668054]{% endif %}" title="Dashboard">
            <i class="fa-solid fa-chart-line w-6 text-center text-lg"></i>
            <span class="ml-3 nav-text font-medium">Dashboard</span>
        </a>""", notif)

# Add Change Password
pw = """<button onclick="openModal('change-password-modal')" class="flex items-center text-gray-600 hover:text-[#668054] group w-full mb-2" title="Change Password">
            <i class="fa-solid fa-key w-6 text-center text-lg"></i>
            <span class="ml-3 nav-text font-medium">Change Password</span>
        </button>
        <a href="/logout" class="flex items-center text-gray-600 hover:text-red-600 group w-full" title="Logout">"""

html = html.replace("""<a href="/logout" class="flex items-center text-gray-600 hover:text-red-600 group w-full" title="Logout">""", pw)

with open("template/admin_sidebar.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched admin_sidebar.html!")
