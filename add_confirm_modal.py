html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Change the submit button to instead open a confirmation modal
old_btn = '<button type="submit" form="editUserForm" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 sm:ml-3 sm:w-auto sm:text-sm">Update User</button>'
new_btn = '<button type="button" onclick="showEditConfirmation()" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 sm:ml-3 sm:w-auto sm:text-sm">Update User</button>'

html = html.replace(old_btn, new_btn)

# 2. Add the confirmation modal HTML before </body>
confirm_modal = '''
    <!-- Edit User Confirmation Modal -->
    <div id="editConfirmModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-[60]">
        <div class="relative top-1/3 mx-auto p-5 border w-80 shadow-2xl rounded-md bg-white">
            <div class="text-center">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 mb-4">
                    <i class="fa-solid fa-triangle-exclamation text-xl text-yellow-600"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900">Confirm Changes</h3>
                <p class="text-sm text-gray-500 mt-2">Are you sure you want to update this user account? This will immediately change their access and profile information.</p>
                <div id="confirmSummary" class="mt-3 bg-gray-50 rounded-md p-3 text-left text-xs text-gray-600 space-y-1"></div>
                <div class="mt-5 flex gap-3 justify-center">
                    <button type="button" onclick="document.getElementById('editConfirmModal').classList.add('hidden')" class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                        Go Back
                    </button>
                    <button type="button" onclick="document.getElementById('editConfirmModal').classList.add('hidden'); document.getElementById('editUserForm').submit();" class="px-4 py-2 bg-purple-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-purple-700">
                        Yes, Update
                    </button>
                </div>
            </div>
        </div>
    </div>
'''

if 'id="editConfirmModal"' not in html:
    html = html.replace('</body>', confirm_modal + '\n</body>')

# 3. Add the JS function to show the modal with a summary
confirm_js = '''
          function showEditConfirmation() {
              // Build the full name first
              updateFullName();
              
              var name = document.getElementById('edit_name').value;
              var email = document.getElementById('edit_email').value;
              var role = document.getElementById('edit_role').value;
              
              var summary = document.getElementById('confirmSummary');
              summary.innerHTML = 
                  '<div><span class="font-medium text-gray-700">Name:</span> ' + name + '</div>' +
                  '<div><span class="font-medium text-gray-700">Email:</span> ' + email + '</div>' +
                  '<div><span class="font-medium text-gray-700">New Role:</span> <span class="capitalize font-semibold text-purple-700">' + role + '</span></div>';
              
              document.getElementById('editConfirmModal').classList.remove('hidden');
          }
'''

if 'function showEditConfirmation' not in html:
    html = html.replace('function updateFullName()', confirm_js + '\n          function updateFullName()')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Added confirmation modal!")
