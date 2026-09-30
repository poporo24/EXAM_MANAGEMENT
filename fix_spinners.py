import os

def fix_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('<i class="fa-solid fa-spinner fa-spin"></i>', '<i class="fa-solid fa-spinner fa-spin mr-2"></i>')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filename}")

fix_file('template/login.html')
fix_file('template/forgot_password.html')
