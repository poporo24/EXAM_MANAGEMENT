with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

old_js = """        async function checkConflict() {
            const exam_id    = document.getElementById('edit_exam_id').value;
            const datetime   = document.getElementById('edit_datetime').value;
            const duration   = document.getElementById('edit_duration').value;
            const room_id    = document.getElementById('edit_room_id').value;
            const proctor_id = document.getElementById('edit_proctor_id').value;
            if (!datetime || !duration || !room_id || !proctor_id) return;"""

new_js = """        async function checkConflict() {
            const exam_id    = document.getElementById('edit_exam_id').value;
            const datetime   = document.getElementById('edit_datetime').value;
            const duration   = document.getElementById('edit_duration').value;
            const room_id    = document.getElementById('edit_room_id').value;
            const proctor_id = document.getElementById('edit_proctor_id').value;
            
            // If date/duration is missing, abort. We can check section conflicts without room/proctor!
            if (!datetime || !duration) return;"""

html = html.replace(old_js, new_js)

old_body = """body: JSON.stringify({ exam_id, exam_datetime: datetime, duration_minutes: Math.round(parseFloat(duration) * 60), room_id: parseInt(room_id), instructor_id: parseInt(proctor_id) })"""
new_body = """body: JSON.stringify({ exam_id, exam_datetime: datetime, duration_minutes: Math.round(parseFloat(duration) * 60), room_id: parseInt(room_id) || 0, instructor_id: parseInt(proctor_id) || 0 })"""

html = html.replace(old_body, new_body)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched checkConflict JS")
