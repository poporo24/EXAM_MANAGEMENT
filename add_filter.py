import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
                    <!-- Action buttons -->
                    <div class="flex gap-2 flex-wrap items-center">
                        <select onchange="window.location.href='/schedule?section=' + encodeURIComponent(this.value)"
                                class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm" title="Filter by Section">
                            <option value="">All Sections</option>
                            {% for s in all_sections %}
                            <option value="{{ s }}" {% if filter_section == s %}selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                        </select>
                        <button onclick="window.print()"'''

content = content.replace('''                    <!-- Action buttons -->
                    <div class="flex gap-2 flex-wrap">
                        <button onclick="window.print()"''', replacement)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
