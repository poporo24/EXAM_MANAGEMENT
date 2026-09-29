import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

try:
    fb_user = auth.get_user_by_email('jpbaltazar23-0368@cca.edu.ph')
    print("Found! UID:", fb_user.uid)
    print("Disabled:", fb_user.disabled)
except Exception as e:
    print("Error:", e)
