import re

html_path = 'template/register.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the old section input with a datalist-powered input
old_section = '''<input type="text" name="section" id="section" class="focus:ring-[#668054] focus:border-[#668054] block w-full pl-10 sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="e.g. BSCS-3A">'''

new_section = '''<input list="section_list" type="text" name="section" id="section" class="focus:ring-[#668054] focus:border-[#668054] block w-full pl-10 sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="Search or type section... e.g. BSCS-3A" autocomplete="off">
                        <datalist id="section_list">
                            {% for sec in sections %}
                                <option value="{{ sec }}"></option>
                            {% endfor %}
                        </datalist>'''

if old_section in html:
    html = html.replace(old_section, new_section)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated register.html with searchable dropdown")
else:
    print("Could not find old section input in register.html!")
