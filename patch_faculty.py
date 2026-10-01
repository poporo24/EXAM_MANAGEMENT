with open("template/faculty.html", "r", encoding="utf-8") as f:
    html = f.read()

old_name_field = """                        <div>
                            <label class="block text-sm font-medium text-gray-700">Full Name</label>
                            <input type="text" name="name" id="edit_inst_name" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                        </div>"""

new_name_fields = """                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Last Name</label>
                                <input type="text" name="last_name" id="edit_inst_last" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">First Name</label>
                                <input type="text" name="first_name" id="edit_inst_first" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Middle Name</label>
                                <input type="text" name="middle_name" id="edit_inst_middle" class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. M.">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Suffix (Optional)</label>
                                <input type="text" name="suffix" id="edit_inst_suffix" class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. Jr.">
                            </div>
                        </div>"""

# Replace in faculty.html
if old_name_field in html:
    html = html.replace(old_name_field, new_name_fields)
    with open("template/faculty.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched faculty.html HTML")
else:
    print("Could not find old_name_field in faculty.html")

# Now update the JS in faculty.html
old_js = """        function openEditInstructorModal(id, name, inst_id, building, is_pwd, subjects) {
            document.getElementById('editInstructorForm').action = '/faculty/' + id + '/edit';
            document.getElementById('edit_inst_name').value = name;"""

new_js = """        function openEditInstructorModal(id, name, inst_id, building, is_pwd, subjects) {
            document.getElementById('editInstructorForm').action = '/faculty/' + id + '/edit';
            
            // Parse "Lastname, Firstname M. Suffix" back into individual fields
            var lastName = '', firstName = '', middleName = '', suffix = '';
            if (name.includes(',')) {
                var commaIdx = name.indexOf(',');
                lastName = name.substring(0, commaIdx).trim();
                var rest = name.substring(commaIdx + 1).trim().split(' ').filter(Boolean);
                var suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV', 'V'];
                if (rest.length > 1 && suffixes.indexOf(rest[rest.length - 1]) !== -1) { suffix = rest.pop(); }
                if (rest.length > 1 && rest[rest.length - 1].length <= 3 && rest[rest.length - 1].endsWith('.')) { middleName = rest.pop().replace('.', ''); }
                firstName = rest.join(' ');
            } else { firstName = name; }
            
            document.getElementById('edit_inst_last').value = lastName;
            document.getElementById('edit_inst_first').value = firstName;
            document.getElementById('edit_inst_middle').value = middleName;
            document.getElementById('edit_inst_suffix').value = suffix;"""

with open("template/faculty.html", "r", encoding="utf-8") as f:
    html = f.read()

if old_js in html:
    html = html.replace(old_js, new_js)
    with open("template/faculty.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched faculty.html JS")
else:
    print("Could not find old_js in faculty.html")
