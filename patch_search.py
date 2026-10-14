with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# We will match the entire select block
pattern = r"<select onchange=\"window\.location\.href='/schedule\?section=' \+ encodeURIComponent\(this\.value\)\".*?</select>"

replacement = """<div class="relative">
                            <input list="sectionList" 
                                   placeholder="Search section..."
                                   value="{{ filter_section if filter_section else '' }}"
                                   onchange="let v = this.value; if(v === 'All Sections') v = ''; window.location.href='/schedule?section=' + encodeURIComponent(v)"
                                   onfocus="this.value=''"
                                   class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm w-48" 
                                   title="Filter by Section">
                            <datalist id="sectionList">
                                <option value="All Sections"></option>
                                {% for s in all_sections %}
                                <option value="{{ s }}"></option>
                                {% endfor %}
                            </datalist>
                        </div>"""

html = re.sub(pattern, replacement, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Replaced dropdown with searchable datalist!")
