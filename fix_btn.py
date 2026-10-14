import re
with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

new_chip = """                <!-- Exam identity chip -->
                <div class="px-6 pt-4 pb-0">
                    <div class="flex items-center justify-between gap-2 bg-[#eef4ea] border border-[#c3d9b8] rounded-lg px-4 py-2.5">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-book-open text-[#668054]"></i>
                            <div>
                                <p id="edit_subject_label" class="text-sm font-semibold text-gray-800">-</p>
                                <p id="edit_section_label" class="text-xs text-gray-500"></p>
                            </div>
                        </div>
                        <button type="button" onclick="autoSchedule()" class="shrink-0 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition-colors">
                            <i class="fa-solid fa-wand-magic-sparkles mr-1"></i> Auto-Schedule
                        </button>
                    </div>
                </div>"""

# Find the block and replace
html = re.sub(r'<!-- Exam identity chip -->.*?</div>\s*</div>\s*</div>', new_chip, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched button")
