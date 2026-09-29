import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)

email = 'jpbaltazar23-0368@cca.edu.ph'
new_password = 'SuperAdmin@2024'

try:
    fb_user = auth.get_user_by_email(email)
    print(f"Found user - UID: {fb_user.uid}, Disabled: {fb_user.disabled}")
    
    # Force reset password and re-enable if disabled
    auth.update_user(
        fb_user.uid,
        password=new_password,
        disabled=False,
        email_verified=True
    )
    print(f"[FIXED] Password reset to: {new_password}")
    print(f"        Account enabled and email verified!")
    
except auth.UserNotFoundError:
    print("[NOT FOUND] Creating fresh account...")
    new_user = auth.create_user(
        email=email,
        password=new_password,
        display_name='CCA Super Admin',
        email_verified=True
    )
    print(f"[CREATED] UID: {new_user.uid}")
    print(f"          Password: {new_password}")
except Exception as e:
    print(f"Error: {e}")
