import glob

new_init = """sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.sidebar-header-container').forEach(h => {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                });"""

new_init_dashboard = """                const texts = sidebar.querySelectorAll('.nav-text');
                texts.forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.sidebar-header-container').forEach(h => {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                });"""

for filepath in glob.glob("template/*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    patched = False
    
    # 1. Standard one-liner
    if "sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));" in content and "document.querySelectorAll('.sidebar-header-container')" not in content:
        content = content.replace("sidebar.querySelectorAll('.nav-text').forEach(el => el.classList.add('hidden'));", new_init)
        patched = True
        
    # 2. Dashboard multiline
    dashboard_str = "const texts = sidebar.querySelectorAll('.nav-text');\n                texts.forEach(el => el.classList.add('hidden'));"
    if dashboard_str in content and "document.querySelectorAll('.sidebar-header-container')" not in content:
        content = content.replace(dashboard_str, new_init_dashboard)
        patched = True

    if patched:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched init in {filepath}")

