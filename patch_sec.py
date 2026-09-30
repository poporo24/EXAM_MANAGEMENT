import re

with open("template/secretary_sidebar.html", "r", encoding="utf-8") as f:
    sec = f.read()

sec = re.sub(
    r'<div class="h-16 flex items-center justify-between px-4 border-b border-gray-200">\s*<div class="flex items-center gap-3 overflow-hidden whitespace-nowrap">\s*<i class="fa-solid fa-graduation-cap text-2xl text-\[#668054\]"></i>\s*<span class="font-bold text-lg nav-text">CCA Exams</span>\s*</div>',
    '<div class="h-16 flex items-center justify-between px-4 border-b border-gray-200 sidebar-header-container">\n            <div class="flex items-center gap-3 overflow-hidden whitespace-nowrap nav-text">\n                <i class="fa-solid fa-graduation-cap text-2xl text-[#668054]"></i>\n                <span class="font-bold text-lg">CCA Exams</span>\n            </div>',
    sec
)

with open("template/secretary_sidebar.html", "w", encoding="utf-8") as f:
    f.write(sec)
print("Patched sec sidebar")
