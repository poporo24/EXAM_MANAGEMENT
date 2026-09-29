import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
                    <!-- Action buttons -->
                    <div class="flex gap-2 flex-wrap items-center">
                        <form action="/admin/print_section" method="GET" target="_blank" class="flex gap-2 items-center mr-2">
                            <select name="section" required class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm" title="Select Section to Print">
                                <option value="">Select Section to Print...</option>
                                {% for s in all_sections %}
                                <option value="{{ s }}">{{ s }}</option>
                                {% endfor %}
                            </select>
                            <button type="submit" class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors shadow-sm">
                                <i class="fa-solid fa-print"></i> Print List format
                            </button>
                        </form>

                        <select onchange="window.location.href='/schedule?section=' + encodeURIComponent(this.value)"
'''

content = content.replace('''                    <!-- Action buttons -->
                    <div class="flex gap-2 flex-wrap items-center">
                        <select onchange="window.location.href='/schedule?section=' + encodeURIComponent(this.value)"''', replacement)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
