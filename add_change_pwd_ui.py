html_path = 'template/settings.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

change_pwd_html = '''
                  <!-- Change Password Settings -->
                  <div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
                      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                          <h2 class="font-semibold text-gray-800">Change My Password</h2>
                          <p class="text-sm text-gray-500 mt-1">Update your personal account password. This applies to both the system and Firebase.</p>
                      </div>
                      <div class="p-6">
                          <form method="POST" action="/settings/change_password" class="space-y-4 max-w-md">
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">Current Password</label>
                                  <input type="password" name="current_password" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                              </div>
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">New Password</label>
                                  <input type="password" name="new_password" required pattern="(?=.*\d)(?=.*[A-Z]).{8,}" title="Must contain at least one number and one uppercase letter, and at least 8 or more characters" class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                              </div>
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                                  <input type="password" name="confirm_password" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                              </div>
                              <div class="pt-2">
                                  <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#526b42]">
                                      Change Password
                                  </button>
                              </div>
                          </form>
                      </div>
                  </div>
'''

# Insert it before the 'Test Configuration' block which has the mt-8 margin
target = '                  <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">'
if 'Change My Password' not in html:
    html = html.replace('<div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden mt-8">', change_pwd_html + '\n                  <div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden mt-8">')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added Change Password UI to settings.html!")
else:
    print("Change Password UI already exists!")
