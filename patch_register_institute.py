with open("template/register.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

old_inst = """<div>
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

new_inst = """<div>
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

if old_inst in html:
    html = html.replace(old_inst, new_inst)
    with open("template/register.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched register.html!")
else:
    print("Could not find old_inst")
