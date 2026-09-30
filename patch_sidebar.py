with open("template/admin_sidebar.html", "r", encoding="utf-8") as f:
    admin = f.read()

old_logo = """    <div class="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">
            <i class="fa-solid fa-graduation-cap text-2xl text-[#668054]"></i>
            <span class="font-bold text-lg nav-text">CCA Exams</span>
        </div>"""

new_logo = """    <div class="h-16 flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container">
        <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text">
            <i class="fa-solid fa-graduation-cap text-2xl text-[#668054]"></i>
            <span class="font-bold text-lg">CCA Exams</span>
        </div>"""

if old_logo in admin:
    admin = admin.replace(old_logo, new_logo)
    with open("template/admin_sidebar.html", "w", encoding="utf-8") as f:
        f.write(admin)
    print("Patched admin sidebar")
else:
    print("Could not patch admin sidebar")

with open("template/secretary_sidebar.html", "r", encoding="utf-8") as f:
    sec = f.read()

if old_logo in sec:
    sec = sec.replace(old_logo, new_logo)
    with open("template/secretary_sidebar.html", "w", encoding="utf-8") as f:
        f.write(sec)
    print("Patched sec sidebar")
else:
    print("Could not patch sec sidebar")

# Update toggleSidebar logic in dashboard.html, reports.html, etc.
import os, glob

for filepath in glob.glob("template/*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "function toggleSidebar()" in content:
        # Check if we need to add centering logic
        old_js = """            sidebar.classList.toggle('w-16');
            mainContent.classList.toggle('ml-64');
            mainContent.classList.toggle('ml-16');"""
            
        new_js = """            sidebar.classList.toggle('w-16');
            mainContent.classList.toggle('ml-64');
            mainContent.classList.toggle('ml-16');
            
            const headers = document.querySelectorAll('.sidebar-header-container');
            headers.forEach(h => {
                if (sidebar.classList.contains('w-16')) {
                    h.classList.remove('justify-between');
                    h.classList.add('justify-center');
                } else {
                    h.classList.add('justify-between');
                    h.classList.remove('justify-center');
                }
            });"""
            
        if old_js in content and "sidebar-header-container" not in content:
            content = content.replace(old_js, new_js)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Patched JS in {filepath}")

