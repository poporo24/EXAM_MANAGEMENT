import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

firebase_init = '''
import firebase_admin
from firebase_admin import credentials, auth as fb_auth

try:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)
except ValueError:
    pass # Already initialized
'''

# Put it right above the app = Flask line
content = content.replace("app = Flask(__name__, template_folder='template')", firebase_init + "\napp = Flask(__name__, template_folder='template')")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected fb_auth")
