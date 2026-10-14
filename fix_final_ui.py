import re

with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove duplicate checkboxes
duplicate_pattern = r"""(\s*<div class="px-6 mt-3">\s*<label class="flex items-center gap-2 text-sm text-gray-700 bg-blue-50 border border-blue-200 p-2.5 rounded-lg cursor-pointer">\s*<input type="checkbox" id="sync_all_sections".*?</div>){2,}"""

# We just find the exact block and replace all occurrences with a single one.
single_block = """                  <div class="px-6 mt-3">
                      <label class="flex items-center gap-2 text-sm text-gray-700 bg-blue-50 border border-blue-200 p-2.5 rounded-lg cursor-pointer">
                          <input type="checkbox" id="sync_all_sections" name="sync_all_sections" value="1" class="rounded text-blue-600 focus:ring-blue-500">
                          <span><i class="fa-solid fa-link text-blue-500 mr-1"></i> Sync Date &amp; Time to <b>ALL</b> sections of this subject</span>
                      </label>
                  </div>"""

# Brute force remove ALL of them, then add ONE back.
html = re.sub(r'\s*<div class="px-6 mt-3">\s*<label class="flex items-center gap-2 text-sm text-gray-700 bg-blue-50 border border-blue-200 p-2.5 rounded-lg cursor-pointer">\s*<input type="checkbox" id="sync_all_sections".*?</div>', '', html, flags=re.DOTALL)

# Now add exactly one back before <!-- Conflict warning -->
html = html.replace("<!-- Conflict warning -->", single_block + "\n                  <!-- Conflict warning -->")


# 2. Inject Auto-Schedule Button
# The chip div ends with </div>\s*</div>\s*</div> before the conflict warning or sync checkbox.
old_chip = r'(<!-- Exam identity chip -->\s*<div class="px-6 pt-4 pb-0">\s*<div class="flex items-center gap-2 bg-\[#eef4ea\] border border-\[#c3d9b8\] rounded-lg px-4 py-2\.5">.*?</div>\s*</div>\s*</div>)'

def chip_repl(match):
    s = match.group(1)
    # Change "flex items-center gap-2" to "flex items-center justify-between gap-2"
    s = s.replace('class="flex items-center gap-2', 'class="flex items-center justify-between gap-2')
    # Wrap the icon and text in their own flex div
    s = s.replace('<i class="fa-solid', '<div class="flex items-center gap-2">\n                              <i class="fa-solid')
    # Close that div and add the button right before the closing of the main flex div
    s = re.sub(r'(</div>\s*)(</div>\s*</div>)$', r'\1</div>\n                              <button type="button" onclick="autoSchedule()" class="shrink-0 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition-colors"><i class="fa-solid fa-wand-magic-sparkles mr-1"></i> Auto-Schedule</button>\n                          \2', s)
    return s

html = re.sub(old_chip, chip_repl, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Fixed duplicate checkboxes and injected Auto-Schedule")
