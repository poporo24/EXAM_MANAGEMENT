html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''          function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              document.getElementById('edit_name').value = name;'''

new_js = '''          function openEditUserModal(id, name, email, role, section, institute_id, is_super_admin) {
              document.getElementById('editUserForm').action = '/super_admin/edit_user/' + id;
              
              // Parse "Lastname, Firstname MI. Suffix" back into individual fields
              var lastName = '', firstName = '', middleName = '', suffix = '';
              if (name.includes(',')) {
                  var commaIdx = name.indexOf(',');
                  lastName = name.substring(0, commaIdx).trim();
                  var rest = name.substring(commaIdx + 1).trim().split(' ').filter(Boolean);
                  var suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV', 'V'];
                  if (rest.length > 1 && suffixes.indexOf(rest[rest.length - 1]) !== -1) {
                      suffix = rest.pop();
                  }
                  if (rest.length > 1 && rest[rest.length - 1].length === 2 && rest[rest.length - 1].endsWith('.')) {
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
              document.getElementById('edit_name').value = name;'''

if old_js in html:
    html = html.replace(old_js, new_js)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed openEditUserModal JS!")
else:
    print("FAILED - could not find old JS block")
