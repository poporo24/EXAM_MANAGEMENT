import re

html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add the button to the header
old_header = '''<header class="bg-white shadow-sm h-16 flex items-center justify-between px-8 z-10 sticky top-0">
            <h1 class="text-xl font-semibold text-gray-800">User Management</h1>
        </header>'''

new_header = '''<header class="bg-white shadow-sm h-16 flex items-center justify-between px-8 z-10 sticky top-0">
            <h1 class="text-xl font-semibold text-gray-800">User Management</h1>
            <button onclick="toggleModal('updateEmailModal')" class="bg-[#668054] text-white px-4 py-2 rounded shadow hover:bg-[#526b42] text-sm font-medium flex items-center gap-2">
                <i class="fa-solid fa-envelope"></i> Update My Email
            </button>
        </header>'''

if old_header in html:
    html = html.replace(old_header, new_header)

# 2. Add the modal
modal_html = '''
    <!-- Update Email Modal -->
    <div id="updateEmailModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div class="mt-3 text-center">
                <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                    <i class="fa-solid fa-envelope text-xl text-[#668054]"></i>
                </div>
                <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">Update Superadmin Email</h3>
                <div class="mt-2 px-2 py-3 text-left">
                    <p class="text-xs text-gray-500 mb-4 text-center">Change your email address so you can receive Firebase password reset links. Must be a @cca.edu.ph address.</p>
                    <form action="/super_admin/update_email" method="POST" id="updateEmailForm">
                        <label class="block text-sm font-medium text-gray-700">New Email Address</label>
                        <input type="email" name="new_email" required pattern=".*@cca\.edu\.ph$" title="Must be @cca.edu.ph" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-[#668054] focus:border-[#668054] sm:text-sm" placeholder="your.name@cca.edu.ph">
                        <div class="mt-6 flex justify-end gap-3">
                            <button type="button" onclick="toggleModal('updateEmailModal')" class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
                            <button type="submit" class="bg-[#668054] border border-transparent rounded-md shadow-sm py-2 px-4 text-sm font-medium text-white hover:bg-[#526b42]">Save</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
'''

if 'id="updateEmailModal"' not in html:
    html = html.replace('</body>', modal_html + '\n</body>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated super_admin.html with update email modal")
