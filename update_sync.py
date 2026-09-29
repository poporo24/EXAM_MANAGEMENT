import os
import re

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Update admin_change_password to update Firebase
admin_pw = '''
            cur = db.cursor()
            hashed = _bcrypt.hashpw(new_password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, user_id))
            db.commit()
            
            # --- FIREBASE SYNC ---
            try:
                from firebase_admin import auth as fb_auth
                fb_auth.update_user(str(user_id), password=new_password)
            except Exception as e:
                print(f"Failed to update Firebase password: {e}")
            # ---------------------
'''
content = re.sub(r'cur = db\.cursor\(\).*?db\.commit\(\)', admin_pw.strip(), content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
