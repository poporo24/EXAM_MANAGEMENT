import os

filepath = 'template/forgot_password.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the duplicate text
content = content.replace('<form id="forgot-form" action="#" class="space-y-6" onsubmit="handleReset(event)"> class="space-y-6">', '<form id="forgot-form" action="#" class="space-y-6" onsubmit="handleReset(event)">')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed stray HTML text.")
