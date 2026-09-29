import os
import glob

# Remove overflow-hidden from body in login and forgot_password
for file in ['template/login.html', 'template/forgot_password.html', 'template/reset_password.html']:
    if not os.path.exists(file): continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix body
    content = content.replace('overflow-hidden', 'overflow-y-auto p-4 sm:p-0')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed auth pages")
