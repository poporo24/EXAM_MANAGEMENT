import os

filepath = 'template/forgot_password.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the error message more verbose
content = content.replace('let msg = "Error sending email.";', 'let msg = "Error sending email: " + error.message;')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated error logging in forgot_password.html")
