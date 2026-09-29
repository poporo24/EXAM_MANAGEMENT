import os

filepath = 'template/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the error message more verbose
content = content.replace('let msg = "Invalid email or password.";', 'let msg = "Error: " + error.message;')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated error logging in login.html")
