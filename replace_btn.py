import re

with open('template/register.html', 'r', encoding='utf-8') as f:
    data = f.read()

# Replace the specific button HTML
old_btn = '''<button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#668054] hover:bg-[#829c74] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#668054] transition-colors">
                    Register Account
                </button>'''

new_btn = '''<button type="button" onclick="openPrivacyModal()" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#668054] hover:bg-[#829c74] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#668054] transition-colors">
                    Register Account
                </button>'''

data = data.replace(old_btn, new_btn)

with open('template/register.html', 'w', encoding='utf-8') as f:
    f.write(data)
