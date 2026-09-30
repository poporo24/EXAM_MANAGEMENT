import os
import re

js_code = """
<script>
    function togglePassword(btn) {
        const container = btn.parentElement;
        const input = container.querySelector('input');
        const icon = btn.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
</script>
"""

icon_html = """<div class="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer" onclick="togglePassword(this)">
    <i class="fa-regular fa-eye text-gray-400 hover:text-gray-600"></i>
</div>"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # If it already has togglePassword, we might have processed it
    if 'togglePassword' in html:
        return

    # Find all inputs with type="password"
    # We will use a regex substitution with a replacement function
    def replacer(match):
        full_input = match.group(0)
        # Add pr-10 if not present
        if 'class="' in full_input:
            if 'pr-10' not in full_input:
                full_input = re.sub(r'class="([^"]*)"', r'class="\1 pr-10"', full_input, count=1)
        else:
            full_input = full_input.replace('<input ', '<input class="pr-10" ')
            
        # We wrap it in a relative div. Since some (like login) are ALREADY inside a relative div, 
        # wrapping it again in a relative div is harmless! (A relative div inside a relative div just establishes a new coordinate system for the icon).
        # Wait, if we wrap it in a relative div, we might break flex/grid layouts if the input was a direct child of a grid with specific styling. But in Tailwind, wrapping an input in a block div is usually fine, especially if we add w-full.
        
        # Actually, let's look at login.html:
        # <div class="mt-1 relative rounded-md shadow-sm">
        #     <div class="...">icon</div>
        #     <input ... class="block w-full ...">
        # </div>
        # If we wrap the input:
        # <div class="mt-1 relative rounded-md shadow-sm">
        #     <div class="...">icon</div>
        #     <div class="relative w-full"> <input ...> <icon> </div>
        # </div>
        # This will work perfectly fine!
        
        return f'<div class="relative w-full">{full_input}{icon_html}</div>'
        
    new_html = re.sub(r'<input[^>]*type=[\'"]password[\'"][^>]*>', replacer, html, flags=re.IGNORECASE)
    
    if new_html != html:
        # Add JS before </body>
        new_html = new_html.replace('</body>', js_code + '\n</body>')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"Updated {filepath}")

for root, _, files in os.walk('template'):
    for file in files:
        if file.endswith('.html'):
            process_file(os.path.join(root, file))

print("Done")
