import re

with open("template/settings.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix Scheduling Engine Settings
html = re.sub(
    r'(<p class="text-xs text-gray-500 mt-1">Maximum hours a proctor can serve without a break\.</p>\s*</div>\s*</div>\s*</div>\s*)</div>',
    r'\1<div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">\n<button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">Save Scheduling Settings</button>\n</div>\n</form>',
    html
)

with open("template/settings.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Regex fixed scheduling form!")
