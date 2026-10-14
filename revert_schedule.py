with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# Revert Filter Section
filter_pattern = r'<div class="relative inline-block">\s*<input type="text" list="filterSectionList".*?</datalist>\s*</div>'
filter_replacement = """<select onchange="window.location.href='/schedule?section=' + encodeURIComponent(this.value)" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm w-40" title="Filter by Section">
                            <option value="">All Sections</option>
                            {% for s in all_sections %}
                            <option value="{{ s }}" {% if filter_section == s %}selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                        </select>"""
html = re.sub(filter_pattern, filter_replacement, html, flags=re.DOTALL)

# Revert Print Section
print_pattern = r'<div class="relative inline-block mr-2">\s*<input type="text" name="section" list="printSectionList".*?</datalist>\s*</div>'
print_replacement = """<select name="section" required class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm w-48" title="Select Section to Print">
                                <option value="">Select Section to Print...</option>
                                {% for s in all_sections %}
                                <option value="{{ s }}">{{ s }}</option>
                                {% endfor %}
                            </select>"""
html = re.sub(print_pattern, print_replacement, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Reverted schedule.html!")
