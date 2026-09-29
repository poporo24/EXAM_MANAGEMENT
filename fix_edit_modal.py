import re

html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace the single Full Name input with 4 separate fields
old_name_field = '''                        <div>
                              <label class="block text-sm font-medium text-gray-700">Full Name</label>
                              <input type="text" name="name" id="edit_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                          </div>'''

new_name_fields = '''                        <div class="grid grid-cols-2 gap-3">
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">First Name</label>
                                  <input type="text" id="edit_first_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="First Name">
                              </div>
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">Last Name</label>
                                  <input type="text" id="edit_last_name" required class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="Last Name">
                              </div>
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">Middle Name <span class="text-xs text-gray-400">(Optional)</span></label>
                                  <input type="text" id="edit_middle_name" class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="Middle Name">
                              </div>
                              <div>
                                  <label class="block text-sm font-medium text-gray-700">Suffix <span class="text-xs text-gray-400">(Optional)</span></label>
                                  <input type="text" id="edit_suffix" class="mt-1 focus:ring-purple-500 block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="Jr., III">
                              </div>
                          </div>
                          <!-- Hidden field to store the combined full_name -->
                          <input type="hidden" name="full_name" id="edit_name">'''

if 'name="name" id="edit_name"' in html:
    html = html.replace(old_name_field, new_name_fields)
    print("Replaced name field!")
else:
    print("Could not find old name field exactly. Trying regex...")
    match = re.search(r'<div>\s*<label[^>]*>Full Name</label>\s*<input[^>]*name="name"[^>]*>\s*</div>', html, re.DOTALL)
    if match:
        html = html.replace(match.group(0), new_name_fields)
        print("Replaced via regex!")
    else:
        print("FAILED - need manual check")

# 2. Update the JS function to split the name and populate fields
old_js = '''          function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              document.getElementById('edit_name').value = name;'''

new_js = '''          function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              
              // Parse the name in "Lastname, Firstname MI. Suffix" format back to fields
              var lastName = '', firstName = '', middleName = '', suffix = '';
              if (name.includes(',')) {
                  var parts = name.split(',');
                  lastName = parts[0].trim();
                  var rest = parts[1].trim().split(' ');
                  // Last token could be suffix (Jr., III, etc.)
                  var suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV', 'V'];
                  if (rest.length > 1 && suffixes.includes(rest[rest.length - 1])) {
                      suffix = rest.pop();
                  }
                  // Second-to-last could be middle initial (single char + dot)
                  if (rest.length > 1 && /^[A-Z]\.$/.test(rest[rest.length - 1])) {
                      middleName = rest.pop().replace('.', '');
                  }
                  firstName = rest.join(' ');
              } else {
                  firstName = name;
              }
              
              document.getElementById('edit_first_name').value = firstName;
              document.getElementById('edit_last_name').value = lastName;
              document.getElementById('edit_middle_name').value = middleName;
              document.getElementById('edit_suffix').value = suffix;
              document.getElementById('edit_name').value = name; // keep hidden field in sync'''

if old_js in html:
    html = html.replace(old_js, new_js)
    print("Updated JS function!")
else:
    print("Could not find old JS function!")

# 3. Add JS to update hidden full_name field when any name field changes
combine_js = '''
          function updateFullName() {
              var firstName = document.getElementById('edit_first_name').value.trim();
              var lastName = document.getElementById('edit_last_name').value.trim();
              var middleName = document.getElementById('edit_middle_name').value.trim();
              var suffix = document.getElementById('edit_suffix').value.trim();
              var mi = middleName ? middleName[0].toUpperCase() + '.' : '';
              var parts = [firstName, mi, suffix].filter(Boolean).join(' ');
              var fullName = lastName ? lastName + ', ' + parts : parts;
              document.getElementById('edit_name').value = fullName;
          }
          ['edit_first_name','edit_last_name','edit_middle_name','edit_suffix'].forEach(function(id) {
              var el = document.getElementById(id);
              if(el) el.addEventListener('input', updateFullName);
          });
'''

if 'function updateFullName' not in html:
    html = html.replace('</script>', combine_js + '\n        </script>', 1)
    print("Added updateFullName JS!")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("All done!")
