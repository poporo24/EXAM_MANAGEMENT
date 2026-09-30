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
    
    if "document.querySelectorAll('.sidebar-header-container')" not in content:
        # Match texts.forEach(el => el.classList.add('hidden'));
        pattern = re.compile(r'texts\.forEach\([^\)]*el\.classList\.add\(\'hidden\'\)[^\)]*\);')
        if pattern.search(content):
            content = pattern.sub(new_code, content)
            patched = True
            
        # Match sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));
        pattern2 = re.compile(r'sidebar\.querySelectorAll\([^)]+\)\.forEach\([^)]+el\.classList\.add\(\'hidden\'\)[^)]*\);')
        if pattern2.search(content):
            content = pattern2.sub(new_code, content)
            patched = True

    if patched:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched init in {filepath}")
