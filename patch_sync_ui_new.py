import re
import os

html_path = 'template/schedule.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add a container for sister sections after the sync checkbox
container_html = """                          <span><i class="fa-solid fa-link text-blue-500 mr-1"></i> Sync Date &amp; Time to <b>ALL</b> sections of this subject</span>
                      </label>
                  </div>
                  <!-- Sister Sections Container -->
                  <div id="sister_sections_container" class="hidden px-6 mt-3 space-y-3 border-l-2 border-purple-300 ml-2 pl-4">
                  </div>"""
html = html.replace('                          <span><i class="fa-solid fa-link text-blue-500 mr-1"></i> Sync Date &amp; Time to <b>ALL</b> sections of this subject</span>\n                      </label>\n                  </div>', container_html)

# Add event listener for sync_all_sections
script_addition = """
        // Handle Sync All checkbox
        const syncCheckbox = document.getElementById('sync_all_sections');
        if (syncCheckbox) {
            syncCheckbox.addEventListener('change', async function() {
                const container = document.getElementById('sister_sections_container');
                if (this.checked) {
                    container.classList.remove('hidden');
                    container.innerHTML = '<p class="text-xs text-gray-500">Loading sister sections...</p>';
                    const exam_id = document.getElementById('edit_exam_id').value;
                    const res = await fetch('/api/sister_sections?exam_id=' + exam_id);
                    const data = await res.json();
                    
                    if (data.sections && data.sections.length > 0) {
                        let html = '<p class="text-xs font-semibold text-gray-600 mb-2">Assign Rooms & Proctors for other sections:</p>';
                        data.sections.forEach(sec => {
                            html += `
                                <div class="grid grid-cols-2 gap-2 p-2 bg-gray-50 rounded-lg border border-gray-200 sister-section-row" data-id="${sec.id}">
                                    <div class="col-span-2 text-xs font-bold text-gray-700">${sec.subject_name} - ${sec.section}</div>
                                    <div>
                                        <select name="sister_room_${sec.id}" class="sister-room w-full border border-gray-300 rounded px-2 py-1 text-xs outline-none" required>
                                            <option value="">Select Room</option>
                                        </select>
                                    </div>
                                    <div>
                                        <select name="sister_inst_${sec.id}" class="sister-inst w-full border border-gray-300 rounded px-2 py-1 text-xs outline-none" required>
                                            <option value="">Select Proctor</option>
                                        </select>
                                    </div>
                                </div>
                            `;
                        });
                        container.innerHTML = html;
                        fetchAvailableResources(); // populate them
                    } else {
                        container.innerHTML = '<p class="text-xs text-gray-500">No other sections found for this subject.</p>';
                    }
                } else {
                    container.classList.add('hidden');
                    container.innerHTML = '';
                }
            });
        }
"""
html = html.replace('/* ── Sidebar Toggle ─────────────────────────────────────── */', script_addition + '\n        /* ── Sidebar Toggle ─────────────────────────────────────── */')

# Update fetchAvailableResources to also populate sister dropdowns
fetch_repl = """        async function fetchAvailableResources() {
            const exam_id = document.getElementById('edit_exam_id').value;
            const dt = document.getElementById('edit_datetime').value;
            const dur = document.getElementById('edit_duration').value;
            if(!dt || !dur) return;

            const res = await fetch('/api/available_resources', {
                method: 'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({exam_id: exam_id, datetime: dt, duration_minutes: dur*60})
            });
            const data = await res.json();
            
            // Populate main selects
            const rSel = document.getElementById('edit_room_id');
            const iSel = document.getElementById('edit_proctor_id');
            
            const currR = rSel.value;
            const currI = iSel.value;
            
            rSel.innerHTML = '<option value="">Select Room</option>';
            data.rooms.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = `${r.room_name} (Cap: ${r.capacity})`;
                rSel.appendChild(opt);
            });
            if(currR) rSel.value = currR;
            
            iSel.innerHTML = '<option value="">Select Proctor</option>';
            data.instructors.forEach(i => {
                const opt = document.createElement('option');
                opt.value = i.id;
                opt.textContent = i.name;
                iSel.appendChild(opt);
            });
            if(currI) iSel.value = currI;
            
            window.lastAvailableRooms = data.rooms;
            window.lastAvailableInstructors = data.instructors;
            
            // Populate sister selects
            document.querySelectorAll('.sister-room').forEach(sel => {
                const cVal = sel.value;
                sel.innerHTML = '<option value="">Select Room</option>';
                data.rooms.forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r.id; opt.textContent = `${r.room_name}`;
                    sel.appendChild(opt);
                });
                if(cVal) sel.value = cVal;
            });
            document.querySelectorAll('.sister-inst').forEach(sel => {
                const cVal = sel.value;
                sel.innerHTML = '<option value="">Select Proctor</option>';
                data.instructors.forEach(i => {
                    const opt = document.createElement('option');
                    opt.value = i.id; opt.textContent = i.name;
                    sel.appendChild(opt);
                });
                if(cVal) sel.value = cVal;
            });
            
            checkConflict();
        }"""
html = re.sub(r'async function fetchAvailableResources\(\)\s*\{.*?(?=async function checkConflict)', fetch_repl + '\n        ', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched schedule.html")

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_code = f.read()

# Add api/sister_sections
api_add = """
@app.route("/api/sister_sections", methods=["GET"])
def get_sister_sections():
    exam_id = request.args.get('exam_id')
    from system.database import open_db
    db = open_db()
    try:
        c = db.cursor(dictionary=True)
        c.execute("SELECT subject_name FROM exams WHERE id=%s", (exam_id,))
        ex = c.fetchone()
        if not ex or not ex.get('subject_name'): return jsonify({'sections': []})
        c.execute("SELECT id, subject_name, section FROM exams WHERE subject_name=%s AND id!=%s ORDER BY section", (ex['subject_name'], exam_id))
        return jsonify({'sections': c.fetchall()})
    finally:
        db.close()
"""
if "/api/sister_sections" not in app_code:
    app_code = app_code.replace('@app.route("/check_edit_conflict", methods=["POST"])', api_add + '\n@app.route("/check_edit_conflict", methods=["POST"])')

# Update edit_exam
app_code = app_code.replace("sync_all     = request.form.get('sync_all_sections') == 'on'", "sync_all     = request.form.get('sync_all_sections') in ['on', '1']")
app_code = app_code.replace("ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str, sync_all=sync_all)", "ok = apply_exam_edit(exam_id, new_room_id, new_inst_id, new_dt_str, sync_all=sync_all, form_data=request.form)")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_code)
print("Patched app.py")

db_path = 'system/database.py'
with open(db_path, 'r', encoding='utf-8') as f:
    db_code = f.read()

db_repl = """def apply_exam_edit(exam_id, new_room_id, new_instructor_id, new_datetime_str, sync_all=False, form_data=None):
    from datetime import datetime as _dt
    db = open_db()
    if not db: return False
    try:
        cursor   = db.cursor()
        cursor_r = db.cursor(dictionary=True)
        try:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            new_dt = _dt.strptime(new_datetime_str, '%Y-%m-%d %H:%M:%S')

        cursor_r.execute(
            "SELECT subject_name, section, instructor_id, room_id, exam_date_time FROM exams WHERE id=%s",
            (exam_id,)
        )
        old = cursor_r.fetchone() or {}
        old_instructor_id = old.get('instructor_id')
        section  = (old.get('section') or '').strip()
        subject  = old.get('subject_name') or 'Exam'
        dt_str   = new_dt.strftime('%b %d, %Y %I:%M %p')

        sister_ids = []
        if sync_all and subject:
            cursor_r.execute("SELECT id FROM exams WHERE subject_name=%s AND id!=%s", (subject, exam_id))
            sister_ids = [r['id'] for r in cursor_r.fetchall()]

        cursor.execute(
            "UPDATE exams SET room_id=%s, instructor_id=%s, exam_date_time=%s, status='Scheduled' WHERE id=%s",
            (new_room_id, new_instructor_id, new_dt, exam_id)
        )
        
        if sync_all and sister_ids:
            for sid in sister_ids:
                s_room = form_data.get(f'sister_room_{sid}') if form_data else None
                s_inst = form_data.get(f'sister_inst_{sid}') if form_data else None
                if s_room and s_inst:
                    cursor.execute(
                        "UPDATE exams SET exam_date_time=%s, room_id=%s, instructor_id=%s, status='Scheduled' WHERE id=%s",
                        (new_dt, s_room, s_inst, sid)
                    )
                else:
                    cursor.execute(
                        "UPDATE exams SET exam_date_time=%s, status='Scheduled' WHERE id=%s",
                        (new_dt, sid)
                    )
        db.commit()"""
db_code = re.sub(r'def apply_exam_edit\(.*?db\.commit\(\)', db_repl, db_code, flags=re.DOTALL)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(db_code)
print("Patched database.py")
