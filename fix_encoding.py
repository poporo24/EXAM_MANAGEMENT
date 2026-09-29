import os

files = ['template/reset_password.html', 'template/forgot_password.html']
for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='windows-1252', errors='replace') as f:
            content = f.read()
        
        # Replace the problematic bullet chars if they got mangled, or just keep them as standard UTF-8 string
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed encoding for {filepath}")
