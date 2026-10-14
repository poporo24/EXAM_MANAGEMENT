with open("template/super_admin.html", "r", encoding="utf-8") as f:
    html = f.read()

old_js = """          function showEditConfirmation() {
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
          });"""

new_js = """          function showEditConfirmation() {
              var firstName = document.getElementById('edit_first_name').value.trim();
              var lastName = document.getElementById('edit_last_name').value.trim();
              var middleName = document.getElementById('edit_middle_name').value.trim();
              var suffix = document.getElementById('edit_suffix').value.trim();
              var mi = middleName ? middleName[0].toUpperCase() + '.' : '';
              var parts = [firstName, mi, suffix].filter(Boolean).join(' ');
              var name = lastName ? lastName + ', ' + parts : parts;

              var email = document.getElementById('edit_email').value;
              var role = document.getElementById('edit_role').value;
              
              var summary = document.getElementById('confirmSummary');
              summary.innerHTML = 
                  '<div><span class="font-medium text-gray-700">Name:</span> ' + name + '</div>' +
                  '<div><span class="font-medium text-gray-700">Email:</span> ' + email + '</div>' +
                  '<div><span class="font-medium text-gray-700">New Role:</span> <span class="capitalize font-semibold text-purple-700">' + role + '</span></div>';
              
              document.getElementById('editConfirmModal').classList.remove('hidden');
          }"""

if old_js in html:
    html = html.replace(old_js, new_js)
    with open("template/super_admin.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed JS in super_admin.html")
else:
    print("Could not find old_js in super_admin.html")
