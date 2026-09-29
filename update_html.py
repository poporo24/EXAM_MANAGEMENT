import re

html_path = 'template/register.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# We need to replace the single full_name block with a grid of 4 inputs
old_block_regex = r'<div>\s*<label for="full_name".*?</div>\s*</div>'

new_block = '''
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label for="first_name" class="block text-sm font-medium text-gray-700">First Name</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" name="first_name" id="first_name" required class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="John Paul">
                    </div>
                </div>
                <div>
                    <label for="last_name" class="block text-sm font-medium text-gray-700">Last Name</label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" name="last_name" id="last_name" required class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="Baltazar">
                    </div>
                </div>
                <div>
                    <label for="middle_name" class="block text-sm font-medium text-gray-700">Middle Name <span class="text-xs text-gray-400">(Optional)</span></label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" name="middle_name" id="middle_name" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="Santos">
                    </div>
                </div>
                <div>
                    <label for="suffix" class="block text-sm font-medium text-gray-700">Suffix <span class="text-xs text-gray-400">(Optional)</span></label>
                    <div class="mt-1 relative rounded-md shadow-sm">
                        <input type="text" name="suffix" id="suffix" class="focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" placeholder="Jr., III">
                    </div>
                </div>
            </div>'''

# Execute replacement
if 'name="full_name"' in html:
    html = re.sub(r'<div>\s*<label for="full_name".*?</div>\s*</div>', new_block, html, flags=re.DOTALL)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated register.html")
else:
    print("full_name not found in register.html!")

