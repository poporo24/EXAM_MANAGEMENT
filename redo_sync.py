with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

old_conflict = """                <!-- Conflict warning -->"""
new_conflict = """                <div class="px-6 mt-3">
                    <label class="flex items-center gap-2 text-sm text-gray-700 bg-blue-50 border border-blue-200 p-2.5 rounded-lg cursor-pointer">
                        <input type="checkbox" id="sync_all_sections" name="sync_all_sections" value="1" class="rounded text-blue-600 focus:ring-blue-500">
                        <span><i class="fa-solid fa-link text-blue-500 mr-1"></i> Sync Date &amp; Time to <b>ALL</b> sections of this subject</span>
                    </label>
                </div>
                <!-- Conflict warning -->"""
if old_conflict in html:
    html = html.replace(old_conflict, new_conflict)

old_auto = """                const resp = await fetch('/api/auto_schedule_exam', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        exam_id, 
                        duration_minutes: Math.round(parseFloat(duration || 1) * 60)
                    })"""
new_auto = """                const sync_all = document.getElementById('sync_all_sections').checked;
                const resp = await fetch('/api/auto_schedule_exam', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        exam_id, 
                        duration_minutes: Math.round(parseFloat(duration || 1) * 60),
                        sync_all: sync_all
                    })"""
if old_auto in html:
    html = html.replace(old_auto, new_auto)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Redid Sync UI")
