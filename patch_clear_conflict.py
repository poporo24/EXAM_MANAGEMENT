with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

old_func = """        async function fetchAvailableResources() {
            const exam_id = document.getElementById('edit_exam_id').value;
            const datetime = document.getElementById('edit_datetime').value;
            const duration = document.getElementById('edit_duration').value;
            if (!datetime || !duration) return;"""

new_func = """        async function fetchAvailableResources() {
            const exam_id = document.getElementById('edit_exam_id').value;
            const datetime = document.getElementById('edit_datetime').value;
            const duration = document.getElementById('edit_duration').value;
            
            // Immediately hide old conflict warnings when user changes date/time!
            document.getElementById('conflictWarning').classList.add('hidden');
            
            if (!datetime || !duration) return;"""

html = html.replace(old_func, new_func)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched conflict warning clear logic")
