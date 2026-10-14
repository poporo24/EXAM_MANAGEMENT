import re

for filename in ['template/login.html', 'template/register.html', 'template/reset_password.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
    
    old = '<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">'
    new = '<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">'
    
    data = data.replace(old, new)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(data)
