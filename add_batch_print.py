import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

route = '''
@app.route("/admin/batch_print_sections")
def admin_batch_print_sections():
    guard = require_role('admin')
    if guard: return guard
    
    all_exams = get_schedule_results()
    scheduled = [e for e in all_exams if e['status'] == 'Scheduled']
    
    from collections import defaultdict
    # Group by section
    sections_dict = defaultdict(list)
    for exam in scheduled:
        sec = exam.get('section', '').strip()
        if sec:
            sections_dict[sec].append(exam)
            
    # For each section, build a grid
    section_grids = {}
    dates_set = set()
    times_set = set()
    
    for sec, exams in sections_dict.items():
        grid = defaultdict(lambda: defaultdict(list))
        for exam in exams:
            dt = exam['exam_date_time']
            if isinstance(dt, str):
                from datetime import datetime
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            d_str = dt.strftime("%Y-%m-%d")
            t_str = dt.strftime("%H:%M")
            exam['_date_label'] = dt.strftime("%a %b %d")
            exam['datetime_raw'] = dt.strftime("%Y-%m-%dT%H:%M")
            exam['duration_minutes'] = exam.get('duration_minutes') or 60
            grid[t_str][d_str].append(exam)
            dates_set.add(d_str)
            times_set.add(t_str)
        section_grids[sec] = grid
        
    dates_list = sorted(list(dates_set))
    times_list = sorted(list(times_set))
    
    date_labels = {}
    for sec, exams in sections_dict.items():
        for e in exams:
            if '_date_label' in e:
                date_labels[e['exam_date_time'].split(' ')[0]] = e['_date_label']
                
    return render_template("batch_print.html",
                           section_grids=section_grids,
                           dates=dates_list,
                           times=times_list,
                           date_labels=date_labels)
'''

content = content.replace('@app.route("/admin/print_section")', route + '\n@app.route("/admin/print_section")')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\app.py', 'w', encoding='utf-8') as f:
    f.write(content)
