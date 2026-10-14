with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

js_code = """
        /* ? Full Auto-Schedule */
        async function autoSchedule() {
            const btn = event.currentTarget;
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Scanning...';
            btn.disabled = true;
            
            const exam_id = document.getElementById('edit_exam_id').value;
            const duration = document.getElementById('edit_duration').value;
            const syncCheckbox = document.getElementById('sync_all_sections');
            const sync_all = syncCheckbox ? syncCheckbox.checked : false;
            
            try {
                const resp = await fetch('/api/auto_schedule_exam', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        exam_id, 
                        duration_minutes: Math.round(parseFloat(duration || 1) * 60),
                        sync_all: sync_all
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
    print("Injected autoSchedule JS")
else:
    print("Already exists")
