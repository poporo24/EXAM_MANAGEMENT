with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# Change the form submission button to button type="button" that triggers JS
old_submit = """                            <button type="submit" class="bg-[#668054] hover:bg-[#526643] text-white px-5 py-2 text-sm font-semibold rounded-lg shadow-sm">
                                <i class="fa-solid fa-floppy-disk mr-1"></i> Save Changes
                            </button>"""
new_submit = """                            <button type="button" onclick="showSaveConfirmation()" class="bg-[#668054] hover:bg-[#526643] text-white px-5 py-2 text-sm font-semibold rounded-lg shadow-sm">
                                <i class="fa-solid fa-floppy-disk mr-1"></i> Save Changes
                            </button>"""
html = html.replace(old_submit, new_submit)

# Add the Confirmation Modal HTML
modal_html = """
    <!-- SAVE CONFIRMATION MODAL -->
    <div id="saveConfirmModal" class="hidden fixed inset-0 z-[60] flex items-center justify-center p-4 bg-gray-900/50 backdrop-blur-sm">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-sm overflow-hidden transform transition-all">
            <div class="p-6 text-center">
                <div class="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mx-auto mb-4">
                    <i class="fa-solid fa-circle-question text-xl"></i>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Confirm Changes</h3>
                <p id="saveConfirmText" class="text-sm text-gray-500 mb-6">Are you sure you want to save these schedule changes?</p>
                <div class="flex gap-3 justify-center">
                    <button type="button" onclick="document.getElementById('saveConfirmModal').classList.add('hidden')" class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
                    <button type="button" onclick="document.getElementById('editScheduleForm').submit()" class="px-4 py-2 bg-[#668054] text-white rounded-lg text-sm font-medium hover:bg-[#526643]">Yes, Save</button>
                </div>
            </div>
        </div>
    </div>
"""

# Insert modal before closing body
html = html.replace("</body>", modal_html + "\n</body>")

# Add JS logic
js_logic = """
        function showSaveConfirmation() {
            // Check if Sync All is checked to give a stronger warning
            const syncChecked = document.getElementById('sync_all_sections') && document.getElementById('sync_all_sections').checked;
            const textEl = document.getElementById('saveConfirmText');
            
            if (syncChecked) {
                textEl.innerHTML = "You are about to modify <b>ALL sections</b> of this subject simultaneously.<br><br>Are you sure you want to proceed?";
                textEl.classList.add('text-orange-600');
            } else {
                textEl.innerHTML = "Are you sure you want to save these schedule changes?";
                textEl.classList.remove('text-orange-600');
            }
            
            document.getElementById('saveConfirmModal').classList.remove('hidden');
        }
"""
html = html.replace("</script>", js_logic + "\n</script>")

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched save confirmation modal")
