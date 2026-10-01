with open("template/super_admin.html", "r", encoding="utf-8") as f:
    html = f.read()

old_name_field = """                    <form id="editUserForm" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Full Name</label>
                            <input type="text" name="name" id="edit_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                        </div>"""

new_name_fields = """                    <form id="editUserForm" method="POST" class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Last Name</label>
                                <input type="text" name="last_name" id="edit_last_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">First Name</label>
                                <input type="text" name="first_name" id="edit_first_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Middle Name</label>
                                <input type="text" name="middle_name" id="edit_middle_name" class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. M.">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Suffix (Optional)</label>
                                <input type="text" name="suffix" id="edit_suffix" class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. Jr.">
                            </div>
                        </div>"""

if old_name_field in html:
    html = html.replace(old_name_field, new_name_fields)
    with open("template/super_admin.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched super_admin.html HTML")
else:
    print("Could not find old_name_field in super_admin.html")

# The JS in super_admin.html already has the parsing logic and populates edit_last_name, etc. but I need to remove document.getElementById('edit_name').value = name;
# Let's check it.
old_js_line = "              document.getElementById('edit_name').value = name;"
if old_js_line in html:
    html = html.replace(old_js_line, "")
    with open("template/super_admin.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched super_admin.html JS")
