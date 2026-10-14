with open('app.py', 'rb') as f:
    data = f.read()

data = data.replace(b'\xc3\xa2\xc5\x93\xe2\x80\xa6', b'\xe2\x9c\x85') # checkmark ✅
data = data.replace(b'\xc3\xa2\xe2\x80\x9a\xc2\xba\xc3\xaf\xc2\xb8\xc2\x8f', b'\xe2\x9a\xa0\xef\xb8\x8f') # warning ⚠️
data = data.replace(b'\xc3\xa2\xe2\x80\x9e\xc2\xb9\xc3\xaf\xc2\xb8\xc2\x8f', b'\xe2\x84\xb9\xef\xb8\x8f') # info ℹ️
data = data.replace(b'\xc3\xb0\xc5\xb8\xde\xab', b'\xf0\x9f\x9a\xab') # block 🚫
data = data.replace(b'\xc3\xb0\xc5\xb8\xef\xbf\xbd\xe2\x80\x98', b'\xf0\x9f\x97\x91\xef\xb8\x8f') # trash 🗑️

# Just find all occurrences of flash(f"..." and manually fix them. Actually, I can just use a regex in python.
import re
def replacer(match):
    prefix = match.group(1)
    return prefix + b' '

# Anything that isn't ASCII starting a flash message gets replaced by an empty space (removing the broken emojis entirely)
data = re.sub(b'(flash\(\s*f?[\'\"])[^\x00-\x7F]+\s+', replacer, data)
data = re.sub(b'(flash\(\s*f?[\'\"])[^\x00-\x7F]+', replacer, data)

with open('app.py', 'wb') as f:
    f.write(data)
