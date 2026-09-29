import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the form I added previously
import re
new_content = re.sub(r'        <div class="mt-8">\n            <div class="relative">[\s\S]*?</form>\n        </div>', '', content)

# Update the register link area to include the irregular portal link
link_replacement = '''        <div class="mt-6 text-center space-y-3">
            <p class="text-sm text-gray-600">
                Don't have an account? 
                <a href="/register" class="font-medium text-[#668054] hover:text-[#829c74]">Register here</a>
            </p>
            <div class="relative py-2">
                <div class="absolute inset-0 flex items-center">
                    <div class="w-full border-t border-gray-200"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                    <span class="px-2 bg-white text-gray-500 font-medium">Irregular Students</span>
                </div>
            </div>
            <a href="/public/timetable" class="inline-flex items-center justify-center w-full py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors">
                <i class="fa-solid fa-magnifying-glass mr-2"></i> Find My Timetable
            </a>
        </div>'''

new_content = re.sub(r'        <div class="mt-6 text-center">\n            <p class="text-sm text-gray-600">\n                Don\'t have an account\? \n                <a href="/register" class="font-medium text-\[#668054\] hover:text-\[#829c74\]">Register here</a>\n            </p>\n        </div>', link_replacement, new_content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\login.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
