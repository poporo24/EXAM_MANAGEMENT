with open("template/register.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

# Fix Institute
old_inst = """<div>
                    <label for="institute_id_text" class="block text-sm font-medium text-gray-700">Institute (Optional)</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" id="institute_id_text" list="instituteList" onchange="updateInstituteId()" placeholder="Select or type..." class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border">
                        <input type="hidden" name="institute_id" id="institute_id">
                        <datalist id="instituteList">
                            {% for inst in institutes %}
                            <option data-id="{{ inst.id }}" value="{{ inst.name }} ({{ inst.code }})">
                            {% endfor %}
                        </datalist>
                    </div>
                </div>
                <script>
                    function updateInstituteId() {
                        const input = document.getElementById('institute_id_text');
                        const hidden = document.getElementById('institute_id');
                        const datalist = document.getElementById('instituteList');
                        hidden.value = '';
                        for (let option of datalist.options) {
                            if (option.value === input.value) {
                                hidden.value = option.getAttribute('data-id');
                                break;
                            }
                        }
                    }
                </script>"""
new_inst = """<div>
                    <label for="institute_id" class="block text-sm font-medium text-gray-700">Institute (Optional)</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <select name="institute_id" id="institute_id" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border">
                            <option value="">Select...</option>
                            {% for inst in institutes %}
                            <option value="{{ inst.id }}">{{ inst.name }} ({{ inst.code }})</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>"""
html = html.replace(old_inst, new_inst)

# Fix Section
old_sec = """<div id="section_container">
                    <label for="section" class="block text-sm font-medium text-gray-700">Section</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" name="section" id="section" list="sectionList" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="e.g. BSCS-3A">
                        <datalist id="sectionList">
                            {% for sec in sections %}
                            <option value="{{ sec }}">
                            {% endfor %}
                        </datalist>
                    </div>
                </div>"""
new_sec = """<div id="section_container">
                    <label for="section" class="block text-sm font-medium text-gray-700">Section</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <select name="section" id="section" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border">
                            <option value="">Select Section...</option>
                            {% for sec in sections %}
                            <option value="{{ sec }}">{{ sec }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>"""
html = html.replace(old_sec, new_sec)

with open("template/register.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Reverted register.html!")
