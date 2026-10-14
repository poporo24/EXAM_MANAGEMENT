with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# 1. Remove Select2 CSS and JS
html = re.sub(r'<!-- Select2 for searchable dropdowns -->\s*<link href="https://cdn\.jsdelivr\.net.*?<style>.*?</style>', '', html, flags=re.DOTALL)
html = re.sub(r'\$\(document\)\.ready\(function\(\) \{\s*\$\(\'\.searchable-select\'\)\.select2.*?\}\);\s*\}\);', '', html, flags=re.DOTALL)

# 2. Re-write the "Filter by Section" dropdown
filter_pattern = r'<select\s+class="searchable-select[^"]*"\s+title="Filter by Section".*?</select>'
filter_replacement = """<div class="relative inline-block">
                            <input type="text" list="filterSectionList" 
                                   placeholder="e.g. BSCS-3A"
                                   value="{{ filter_section if filter_section else '' }}"
                                   onchange="let v = this.value; window.location.href='/schedule?section=' + encodeURIComponent(v)"
                                   onfocus="this.value=''"
                                   class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm w-40" 
                                   title="Filter by Section">
                            <datalist id="filterSectionList">
                                <option value="">All Sections</option>
                                {% for s in all_sections %}
                                <option value="{{ s }}"></option>
                                {% endfor %}
                            </datalist>
                        </div>"""
html = re.sub(filter_pattern, filter_replacement, html, flags=re.DOTALL)

# 3. Re-write the "Select Section to Print..." dropdown
print_pattern = r'<select name="section" required class="searchable-select[^"]*" title="Select Section to Print">.*?</select>'
print_replacement = """<div class="relative inline-block mr-2">
                                <input type="text" name="section" list="printSectionList" required
                                       placeholder="e.g. BSCS-3A"
                                       onfocus="this.value=''"
                                       class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm w-48" 
                                       title="Select Section to Print">
                                <datalist id="printSectionList">
                                    {% for s in all_sections %}
                                    <option value="{{ s }}"></option>
                                    {% endfor %}
                                </datalist>
                            </div>"""
html = re.sub(print_pattern, print_replacement, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Applied datalist successfully!")
