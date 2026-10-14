import re

with open('app.py', 'r', encoding='utf-8') as f:
    data = f.read()

old_code = r'''    session\['last_scheduled_count'\] = len\(result\['scheduled'\]\)
    
    if failed_ids:
        flash\(f"Auto-resolve completed, but \{len\(failed_ids\)\} exam\(s\) could still not be scheduled\.", "warning"\)
    else:
        flash\(" All conflicts have been successfully auto-resolved!", "success"\)
        
    return redirect\(url_for\('schedule_view'\)\)'''

new_code = '''    session['last_scheduled_count'] = len(result['scheduled'])
    
    resolved_info = ""
    if result['scheduled']:
        resolved_details = [f"{e.get('subject_name')} ({e.get('section')})" for e in result['scheduled']]
        resolved_info = " Resolved: " + ", ".join(resolved_details)

    if failed_ids:
        flash(f"Auto-resolve completed, but {len(failed_ids)} exam(s) could still not be scheduled.{resolved_info}", "warning")
    else:
        flash(f"All conflicts have been successfully auto-resolved!{resolved_info}", "success")
        
    return redirect(url_for('schedule_view'))'''

data = re.sub(old_code, new_code, data)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(data)
