import os

files = ['template/login.html', 'template/forgot_password.html']
for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the typo (capital H -> lowercase h at the end)
    content = content.replace('AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwHE', 'AIzaSyCjf-aMcch8I9thXy5Lw1QzWfUX3sOAwhE')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated API Keys!")
