import re

html_path = 'template/register.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_section = r'''<input list="section_list" type="text" name="section" id="section" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="Search or type section... e.g. BSCS-1A" autocomplete="off">
                        <datalist id="section_list">
                            {% for sec in sections %}
                                <option value="{{ sec }}"></option>
                            {% endfor %}
                        </datalist>'''

new_section = '''<select name="section" id="section" required class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border">
                            <option value="">Select...</option>
                            {% for sec in sections %}
                            <option value="{{ sec }}">{{ sec }}</option>
                            {% endfor %}
                        </select>'''

if 'list="section_list"' in html:
    html = re.sub(r'<input list="section_list".*?</datalist>', new_section, html, flags=re.DOTALL)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Changed to native select dropdown!")
else:
    print("Could not find datalist in register.html")
