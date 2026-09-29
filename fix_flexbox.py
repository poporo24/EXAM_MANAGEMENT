import os

files = ['template/login.html', 'template/forgot_password.html', 'template/reset_password.html']
for filepath in files:
    if not os.path.exists(filepath): continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update Body
    content = content.replace('flex items-center justify-center relative overflow-y-auto p-4 sm:p-0', 'relative overflow-y-auto p-4 sm:p-8 flex flex-col')
    
    # Update Inner Div
    content = content.replace('class="z-10 w-full max-w-md bg-white rounded-xl shadow-xl p-8 border border-gray-100"', 'class="z-10 w-full max-w-md bg-white rounded-xl shadow-xl p-8 border border-gray-100 m-auto"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed flexbox cutoff bug")
