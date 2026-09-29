import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

# The DB email is jpbaltazar23-0368@cca.edu.ph
# Check if it exists in Firebase
try:
    fb_user = auth.get_user_by_email('jpbaltazar23-0368@cca.edu.ph')
    print(f"[OK] jpbaltazar23-0368@cca.edu.ph EXISTS in Firebase")
    print(f"     UID: {fb_user.uid}")
except auth.UserNotFoundError:
    print("[MISSING] Not in Firebase - creating now...")
    new_user = auth.create_user(
        email='jpbaltazar23-0368@cca.edu.ph',
        password='SuperAdmin@2024',
        display_name='CCA Super Admin'
    )
    print(f"[CREATED] UID: {new_user.uid}")
    print(f"          Password set to: SuperAdmin@2024")
