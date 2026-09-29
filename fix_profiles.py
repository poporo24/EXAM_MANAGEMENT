import re

# Update admin_sidebar.html
admin_path = 'template/admin_sidebar.html'
with open(admin_path, 'r', encoding='utf-8') as f:
    admin_html = f.read()

old_admin_profile = r'''        <div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">
            <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold">
                A
            </div>
            <div class="ml-3 nav-text">
                <p class="text-sm font-medium text-gray-900">Admin User</p>
                <p class="text-xs text-gray-500">Administrator</p>
            </div>
        </div>'''

new_admin_profile = '''        <div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">
            <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold uppercase">
                {{ session.get('full_name', 'A')[:1] }}
            </div>
            <div class="ml-3 nav-text">
                <p class="text-sm font-medium text-gray-900 truncate w-40" title="{{ session.get('full_name', 'Admin User') }}">{{ session.get('full_name', 'Admin User') }}</p>
                <p class="text-xs text-gray-500">
                    {% if session.get('is_super_admin') %}
                    Super Administrator
                    {% else %}
                    Administrator
                    {% endif %}
                </p>
            </div>
        </div>'''

admin_html = re.sub(old_admin_profile.replace(' ', '\s*'), new_admin_profile, admin_html, flags=re.DOTALL)
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(admin_html)

# Update secretary_sidebar.html
sec_path = 'template/secretary_sidebar.html'
with open(sec_path, 'r', encoding='utf-8') as f:
    sec_html = f.read()

old_sec_profile = r'''              <div class="flex items-center mb-3 overflow-hidden whitespace-nowrap">
                  <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold">S</div>
                  <div class="ml-3 nav-text">
                      <p class="text-sm font-medium text-gray-900">Secretary User</p>
                      <p class="text-xs text-gray-500">Secretary</p>
                  </div>
              </div>'''

# Also fix the Secretary vs College Secretary typo
old_sec_profile2 = r'''              <div class="flex items-center mb-3 overflow-hidden whitespace-nowrap">
                  <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold">S</div>
                  <div class="ml-3 nav-text">
                      <p class="text-sm font-medium text-gray-900">Secretary</p>
                      <p class="text-xs text-gray-500">College Secretary</p>
                  </div>
              </div>'''

new_sec_profile = '''              <div class="flex items-center mb-3 overflow-hidden whitespace-nowrap">
                  <div class="w-8 h-8 rounded-full bg-[#829c74] text-white flex items-center justify-center font-bold uppercase">
                      {{ session.get('full_name', 'S')[:1] }}
                  </div>
                  <div class="ml-3 nav-text">
                      <p class="text-sm font-medium text-gray-900 truncate w-40" title="{{ session.get('full_name', 'College Secretary') }}">{{ session.get('full_name', 'College Secretary') }}</p>
                      <p class="text-xs text-gray-500">College Secretary</p>
                  </div>
              </div>'''

# Just use string replace for safety
# Let's extract the actual block from the file to be perfectly safe
match = re.search(r'<div class="flex items-center mb-3 overflow-hidden whitespace-nowrap">.*?</div>\s*</div>', sec_html, flags=re.DOTALL)
if match:
    sec_html = sec_html.replace(match.group(0), new_sec_profile)
    with open(sec_path, 'w', encoding='utf-8') as f:
        f.write(sec_html)
    print("Fixed both sidebars!")
else:
    print("Could not find secretary profile block")
