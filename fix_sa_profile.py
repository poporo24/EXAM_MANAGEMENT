html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace hardcoded profile block in super_admin sidebar
old_profile = '''              <div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">
                  <div class="w-8 h-8 rounded-full bg-purple-700 text-white flex items-center justify-center font-bold">SA</div>
                  <div class="ml-3 nav-text">
                      <p class="text-sm font-medium text-gray-900">Super Admin</p>
                      <p class="text-xs text-gray-500">System Owner</p>
                  </div>
              </div>'''

new_profile = '''              <div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">
                  <div class="w-8 h-8 rounded-full bg-purple-700 text-white flex items-center justify-center font-bold uppercase">
                      {{ session.get('full_name', 'SA')[:1] }}
                  </div>
                  <div class="ml-3 nav-text">
                      <p class="text-sm font-medium text-gray-900 truncate w-36" title="{{ session.get('full_name', 'Super Admin') }}">
                          {{ session.get('full_name', 'Super Admin') }}
                      </p>
                      <p class="text-xs text-purple-600 font-semibold">Super Administrator</p>
                      <p class="text-xs text-gray-400 truncate w-36">{{ session.get('email', '') }}</p>
                  </div>
              </div>'''

if 'bg-purple-700 text-white flex items-center justify-center font-bold">SA' in html:
    html = html.replace(old_profile, new_profile)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed super_admin.html profile!")
else:
    # Try a more flexible replacement
    import re
    pattern = r'<div class="flex items-center mb-4 overflow-hidden whitespace-nowrap">\s*<div class="w-8 h-8 rounded-full bg-purple-700.*?">SA</div>\s*<div class="ml-3 nav-text">\s*<p class="text-sm font-medium text-gray-900">Super Admin</p>\s*<p class="text-xs text-gray-500">System Owner</p>\s*</div>\s*</div>'
    match = re.search(pattern, html, flags=re.DOTALL)
    if match:
        html = html.replace(match.group(0), new_profile)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("Fixed super_admin.html profile (regex)!")
    else:
        print("Could not find profile block. Manual check needed.")
        print("Looking for:", repr(html[html.find('bg-purple-700'):html.find('bg-purple-700')+200]))
