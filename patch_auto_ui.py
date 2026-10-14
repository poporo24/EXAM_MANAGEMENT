with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add the button below the exam identity chip
old_chip = """                <!-- Exam identity chip -->
                <div class="px-6 pt-4 pb-0">
                    <div class="flex items-center gap-2 bg-[#eef4ea] border border-[#c3d9b8] rounded-lg px-4 py-2.5">
                        <i class="fa-solid fa-book-open text-[#668054]"></i>
                        <div>
                            <p id="edit_subject_label" class="text-sm font-semibold text-gray-800">-</p>
                            <p id="edit_section_label" class="text-xs text-gray-500"></p>
                        </div>
                    </div>
                </div>"""

new_chip = """                <!-- Exam identity chip -->
                <div class="px-6 pt-4 pb-0">
                    <div class="flex items-center justify-between gap-2 bg-[#eef4ea] border border-[#c3d9b8] rounded-lg px-4 py-2.5">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-book-open text-[#668054]"></i>
                            <div>
                                <p id="edit_subject_label" class="text-sm font-semibold text-gray-800">-</p>
                                <p id="edit_section_label" class="text-xs text-gray-500"></p>
                            </div>
                        </div>
                        <button type="button" onclick="autoSchedule()" class="shrink-0 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition-colors">
                            <i class="fa-solid fa-wand-magic-sparkles mr-1"></i> Auto-Schedule
                        </button>
                    </div>
                </div>"""

html = html.replace(old_chip, new_chip)

# Add the JS for autoSchedule()
js_code = """
        /* ? Full Auto-Schedule */
        async function autoSchedule() {
            const btn = event.currentTarget;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Scanning...';
            btn.disabled = true;
            
            const exam_id = document.getElementById('edit_exam_id').value;
            const duration = document.getElementById('edit_duration').value;
            
            try {
                const resp = await fetch('/api/auto_schedule_exam', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        exam_id, 
                        duration_minutes: Math.round(parseFloat(duration || 1) * 60)
                    })
                });
                const data = await resp.json();
                
                if (data.datetime) {
                    // Update Date & Time
                    document.getElementById('edit_datetime').value = data.datetime;
                    // Trigger the fetch for available resources to populate the dropdowns based on this new date
                    await fetchAvailableResources();
                    
                    // Now set the specific Room and Proctor that the algorithm chose
                    document.getElementById('edit_room_id').value = data.room_id;
                    document.getElementById('edit_proctor_id').value = data.instructor_id;
                    
                    // Trigger a final check to ensure the UI is clean
                    await checkConflict();
                    
                    // Briefly flash green to indicate success
                    btn.classList.remove('bg-purple-600', 'hover:bg-purple-700');
                    btn.classList.add('bg-green-600');
                    btn.innerHTML = '<i class="fa-solid fa-check mr-1"></i> Found!';
                    setTimeout(() => {
                        btn.classList.add('bg-purple-600', 'hover:bg-purple-700');
                        btn.classList.remove('bg-green-600');
                        btn.innerHTML = originalHTML;
                        btn.disabled = false;
                    }, 2000);
                } else {
                    alert("Could not find any available slot with a free room and proctor in the next 14 days.");
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                }
            } catch (e) { 
                console.error(e); 
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }
        }
"""

if "function autoSchedule" not in html:
    html = html.replace("</script>\n</body>", js_code + "\n</script>\n</body>")

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched UI for Full Auto-Schedule")
