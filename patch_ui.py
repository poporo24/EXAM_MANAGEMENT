with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's find the Date & Time input in editScheduleModal
old_html = """                        <div class="col-span-2">
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Date &amp; Time</label>
                            <input type="datetime-local" name="exam_datetime" id="edit_datetime" required
                                   onchange="fetchAvailableResources()"
                                   class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none">
                        </div>"""

new_html = """                        <div class="col-span-2 relative">
                            <div class="flex justify-between items-end mb-1">
                                <label class="block text-xs font-semibold text-gray-600">Date &amp; Time</label>
                                <button type="button" onclick="suggestTimes()" class="text-xs text-purple-600 hover:text-purple-800 font-medium">
                                    <i class="fa-solid fa-wand-magic-sparkles"></i> Auto-Suggest
                                </button>
                            </div>
                            <input type="datetime-local" name="exam_datetime" id="edit_datetime" required
                                   onchange="fetchAvailableResources()"
                                   class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none">
                            <div id="suggest_dropdown" class="hidden absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-48 overflow-y-auto">
                                <div class="px-3 py-2 text-xs font-bold text-gray-500 bg-gray-50 border-b">Suggested Available Slots</div>
                                <div id="suggest_list"></div>
                            </div>
                        </div>"""

html = html.replace(old_html, new_html)

# Add the suggestTimes() JavaScript
js_code = """
        /* ? Auto-Suggest Times */
        async function suggestTimes() {
            const btn = event.currentTarget;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
            
            const exam_id = document.getElementById('edit_exam_id').value;
            const duration = document.getElementById('edit_duration').value;
            const room_id = document.getElementById('edit_room_id').value;
            const proctor_id = document.getElementById('edit_proctor_id').value;
            
            try {
                const resp = await fetch('/api/suggest_times', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        exam_id, 
                        duration_minutes: Math.round(parseFloat(duration || 1) * 60),
                        room_id: parseInt(room_id) || 0,
                        instructor_id: parseInt(proctor_id) || 0
                    })
                });
                const data = await resp.json();
                const list = document.getElementById('suggest_list');
                list.innerHTML = '';
                
                if (data.suggestions && data.suggestions.length > 0) {
                    data.suggestions.forEach(s => {
                        const div = document.createElement('div');
                        div.className = 'px-3 py-2 text-sm text-gray-700 hover:bg-[#eef4ea] hover:text-[#668054] cursor-pointer';
                        div.innerText = s.label;
                        div.onclick = () => {
                            document.getElementById('edit_datetime').value = s.datetime;
                            document.getElementById('suggest_dropdown').classList.add('hidden');
                            fetchAvailableResources();
                        };
                        list.appendChild(div);
                    });
                } else {
                    list.innerHTML = '<div class="px-3 py-2 text-sm text-red-500 italic">No available slots found in the next 14 days.</div>';
                }
                
                document.getElementById('suggest_dropdown').classList.remove('hidden');
                
                // Click outside to close
                document.addEventListener('click', function closeSuggest(e) {
                    if (!e.target.closest('.col-span-2.relative')) {
                        document.getElementById('suggest_dropdown').classList.add('hidden');
                        document.removeEventListener('click', closeSuggest);
                    }
                });
                
            } catch (e) { console.error(e); }
            finally {
                btn.innerHTML = originalHTML;
            }
        }
"""

if "function suggestTimes" not in html:
    html = html.replace("</script>\n</body>", js_code + "\n</script>\n</body>")

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched UI for Auto-Suggest")
