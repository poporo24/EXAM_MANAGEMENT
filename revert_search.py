with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

pattern = r'<div class="relative">\s*<input list="sectionList".*?</datalist>\s*</div>'

replacement = """<select onchange="window.location.href='/schedule?section=' + encodeURIComponent(this.value)"
                                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm" title="Filter by Section">
                            <option value="">All Sections</option>
                            {% for s in all_sections %}
                            <option value="{{ s }}" {% if filter_section == s %}selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                        </select>"""

html = re.sub(pattern, replacement, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Reverted to native select!")
