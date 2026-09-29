import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add firebase_admin init if not there
init_block = '''import firebase_admin
from firebase_admin import credentials, auth as fb_auth

try:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)
except ValueError:
    pass # Already initialized
'''
if "firebase_admin.initialize_app" not in content:
    content = content.replace("app = Flask(__name__)", "app = Flask(__name__)\n\n" + init_block)

# Replace login post logic
import re
login_pattern = re.compile(r'@app\.route\("/login", methods=\["GET", "POST"\]\)\ndef login\(\):.*?return render_template\("login\.html", sections=sections\)', re.DOTALL)
match = login_pattern.search(content)

if match:
    # Need to keep the GET part
    get_part = match.group(0)
    
    new_post_part = '''
    
    firebase_token = request.form.get("firebase_token")
    if not firebase_token:
        flash("Firebase authentication failed. Missing token.", "error")
        return redirect(url_for('login'))
        
    try:
        decoded_token = fb_auth.verify_id_token(firebase_token)
        email = decoded_token.get('email')
        
        user = get_user_by_email(email)
        if not user:
            flash("User not found in system.", "error")
            return redirect(url_for('login'))
            
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['name'] = user['full_name']
        session['email'] = user['email']
        session['section'] = user['section']
        session['institute_id'] = user['institute_id']
        
        return _redirect_by_role()
    except Exception as e:
        flash(f"Invalid login session: {str(e)}", "error")
        return redirect(url_for('login'))
'''
    # We replace the entire login function body after the GET part
    # Wait, let's just replace the whole login function cleanly
    
    entire_login_pattern = re.compile(r'@app\.route\("/login", methods=\["GET", "POST"\]\)\ndef login\(\):.*?return _redirect_by_role\(\)', re.DOTALL)
    
    new_login_func = '''@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session and session.get('role'):
            return _redirect_by_role()
        all_exams = get_schedule_results()
        sections = sorted(list(set(e.get('section', '').strip() for e in all_exams if e.get('section', '').strip() and e.get('status') == 'Scheduled')))
        return render_template("login.html", sections=sections)
''' + new_post_part
    
    content = entire_login_pattern.sub(new_login_func, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py with Firebase Auth")
