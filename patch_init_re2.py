import glob
import re

new_code = r"""\g<0>
                document.querySelectorAll('.sidebar-header-container').forEach(h => {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                });"""

for filepath in glob.glob("template/*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    patched = False
    
    if "sidebar-header-container" in content and "h.classList.add('justify-center')" not in content:
        print(f"Skipping {filepath} - doesn't have sidebar-header-container logic but has it in JS? wait...")
        
    if "document.querySelectorAll('.sidebar-header-container').forEach(" not in content:
        if "sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));" in content:
            content = content.replace("sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));", 
"""sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.sidebar-header-container').forEach(h => {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                });""")
            patched = True
        elif "texts.forEach(el => el.classList.add('hidden'));" in content:
            content = content.replace("texts.forEach(el => el.classList.add('hidden'));", 
"""texts.forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.sidebar-header-container').forEach(h => {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                });""")
            patched = True

    if patched:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {filepath}")
