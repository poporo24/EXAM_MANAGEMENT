import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

# Check superadmin specifically
try:
    fb_user = auth.get_user_by_email('superadmin@cca.edu.ph')
    print(f"[OK] superadmin@cca.edu.ph EXISTS in Firebase")
    print(f"     UID: {fb_user.uid}")
    print(f"     Email verified: {fb_user.email_verified}")
    print(f"     Disabled: {fb_user.disabled}")
except auth.UserNotFoundError:
    print("[MISSING] superadmin@cca.edu.ph is NOT in Firebase!")
    # Create it with a default password
    new_user = auth.create_user(
        email='superadmin@cca.edu.ph',
        password='SuperAdmin@2024',
        display_name='CCA Super Admin'
    )
    print(f"[CREATED] Created with password: SuperAdmin@2024")
    print(f"          UID: {new_user.uid}")
