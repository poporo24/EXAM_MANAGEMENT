app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_session = """        session['user_id'] = user['id']
        session['role'] = user['role']
        session['name'] = user['full_name']
        session['email'] = user['email']
        session['section'] = user['section']
        session['institute_id'] = user['institute_id']
        
        return _redirect_by_role()"""

new_session = """        session['user_id']        = user['id']
        session['full_name']      = user['full_name']
        session['role']           = user.get('role', 'student')
        session['email']          = user['email']
        session['section']        = user.get('section', '')
        session['institute_id']   = user.get('institute_id')
        session['instructor_id']  = user.get('instructor_id')
        session['is_super_admin'] = bool(user.get('is_super_admin', 0))
        
        return _redirect_by_role()"""

if old_session in content:
    content = content.replace(old_session, new_session)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed Firebase login session!")
else:
    print("Could not find the old session block!")
