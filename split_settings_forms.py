import re

with open("template/settings.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace the top form with a div wrapper
html = html.replace('<form id="settingsForm" method="POST" action="/settings/save" class="space-y-8">', '<div class="space-y-8">')

# 2. Add form wrapper for Scheduling
html = html.replace(
    '<div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Scheduling Engine Settings</h2>',
    '<form method="POST" action="/settings/save" class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                        <input type="hidden" name="section" value="scheduling">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Scheduling Engine Settings</h2>'
)

# 3. Add Save button for Scheduling and closing form tag
html = html.replace(
    '''<p class="text-xs text-gray-500 mt-1">Minimum rest time between assignments.</p>
                            </div>
                        </div>
                    </div>''',
    '''<p class="text-xs text-gray-500 mt-1">Minimum rest time between assignments.</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Scheduling Settings
                        </button>
                    </div>
                </form>'''
)

# 4. Add form wrapper for Exam Duration Defaults
html = html.replace(
    '<div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Exam Duration Defaults</h2>',
    '<form method="POST" action="/settings/save" class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                        <input type="hidden" name="section" value="duration">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Exam Duration Defaults</h2>'
)

# 5. Add Save button for Exam Duration Defaults and closing form tag
html = html.replace(
    '''<p class="text-xs text-gray-500 mt-1">Default for non-major subjects.</p>
                            </div>
                        </div>
                    </div>''',
    '''<p class="text-xs text-gray-500 mt-1">Default for non-major subjects.</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Duration Settings
                        </button>
                    </div>
                </form>'''
)

# 6. Add form wrapper for SMTP
html = html.replace(
    '<div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Email & SMTP Settings</h2>',
    '<form method="POST" action="/settings/save" class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">\n                        <input type="hidden" name="section" value="smtp">\n                    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">\n                        <h2 class="font-semibold text-gray-800">Email & SMTP Settings</h2>'
)

# 7. Modify SMTP Save button and closing form tag
# The original has this block at the end of SMTP:
html = html.replace(
    '''<div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="button" onclick="openSaveModal()" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save All Settings
                        </button>
                    </div>
                </div>
            </form>''',
    '''<div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Email Settings
                        </button>
                    </div>
                </form>
            </div>'''
)

with open("template/settings.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Split forms in settings.html!")
