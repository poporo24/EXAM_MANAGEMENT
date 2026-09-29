import re
html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = r'''function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              document.getElementById('edit_name').value = name;
              document.getElementById('edit_email').value = email;
              document.getElementById('edit_role').value = role;
              document.getElementById('edit_section').value = section !== 'None' ? section : '';
              document.getElementById('edit_institute').value = institute_id !== 'None' ? institute_id : '';
              document.getElementById('edit_super_admin').checked = is_super_admin === 'True' || is_super_admin === 'true' || is_super_admin === true;'''

new_js = r'''function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              
              // Parse "Lastname, Firstname MI. Suffix" back into individual fields
              var lastName = '', firstName = '', middleName = '', suffix = '';
              if (name.includes(',')) {
                  var commaIdx = name.indexOf(',');
                  lastName = name.substring(0, commaIdx).trim();
                  var rest = name.substring(commaIdx + 1).trim().split(' ').filter(Boolean);
                  var suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV', 'V'];
                  if (rest.length > 1 && suffixes.indexOf(rest[rest.length - 1]) !== -1) { suffix = rest.pop(); }
                  if (rest.length > 1 && rest[rest.length - 1].length === 2 && rest[rest.length - 1].endsWith('.')) { middleName = rest.pop().replace('.', ''); }
                  firstName = rest.join(' ');
              } else { firstName = name; }
              
              if(document.getElementById('edit_first_name')) document.getElementById('edit_first_name').value = firstName;
              if(document.getElementById('edit_last_name')) document.getElementById('edit_last_name').value = lastName;
              if(document.getElementById('edit_middle_name')) document.getElementById('edit_middle_name').value = middleName;
              if(document.getElementById('edit_suffix')) document.getElementById('edit_suffix').value = suffix;
              document.getElementById('edit_name').value = name;
              document.getElementById('edit_email').value = email;
              document.getElementById('edit_role').value = role;
              document.getElementById('edit_section').value = section !== 'None' ? section : '';
              document.getElementById('edit_institute').value = institute_id !== 'None' ? institute_id : '';
              document.getElementById('edit_super_admin').checked = is_super_admin === 'True' || is_super_admin === 'true' || is_super_admin === true;'''

# Use regex to find and replace regardless of whitespace differences
pattern = re.compile(r'function openEditUserModal\(id, name, email, role, section, institute_id, is_super_admin\)\s*\{.*?document\.getElementById\(\'edit_super_admin\'\)\.checked[^;]+;', re.DOTALL)
match = pattern.search(html)
if match:
    html = html.replace(match.group(0), new_js)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed via regex!")
else:
    print("Still not found. Check the JS function manually.")
