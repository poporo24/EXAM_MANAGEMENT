import sys
import re
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

find_block = r'''                                    <div>
                                        <label for="name" class="block text-sm font-medium text-gray-700">Exam Name</label>
                                        <input type="text" name="name" id="name" required class="mt-1 focus:ring-\[#668054\] focus:border-\[#668054\] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                                    </div>'''

content = re.sub(find_block, '', content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
