with open("template/proctor_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix hardcoded name
old_profile = """<div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">
                <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold">P</div>
                <div class="ml-3 nav-text">
                    <p class="text-sm font-medium text-gray-900">Proctor User</p>
                    <p class="text-xs text-gray-500">Proctor</p>
                </div>
            </div>"""
            
new_profile = """<div class="flex items-center mb-3 overflow-hidden whitespace-nowrap">
                <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold uppercase">
                    {{ session.get('full_name', 'P')[:1] }}
                </div>
                <div class="ml-3 nav-text">
                    <p class="text-sm font-medium text-gray-900 truncate w-40" title="{{ session.get('full_name', 'Proctor User') }}">{{ session.get('full_name', 'Proctor User') }}</p>
                    <p class="text-xs text-gray-500">Proctor</p>
                </div>
            </div>"""

html = html.replace(old_profile, new_profile)

# Add Change Password
pw = """<button onclick="openModal('change-password-modal')" class="flex items-center text-gray-600 hover:text-[#668054] group w-full mb-2" title="Change Password">
                <i class="fa-solid fa-key w-6 text-center text-lg"></i>
                <span class="ml-3 nav-text font-medium">Change Password</span>
            </button>
            <a href="/logout" class="flex items-center text-gray-600 hover:text-red-600 group w-full" title="Logout">"""

html = html.replace("""<a href="/logout" class="flex items-center text-gray-600 hover:text-red-600 group w-full" title="Logout">""", pw)

with open("template/proctor_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched proctor_dashboard.html!")
