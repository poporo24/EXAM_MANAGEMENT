import sys
path = sys.argv[1] if len(sys.argv) > 1 else 'app.py'
with open(path, 'r', encoding='utf-8', newline='') as f:
    text = f.read()

if '_MAIL_POOL' in text:
    print('Already patched')
    sys.exit(0)

text = text.replace(
    "threading.Thread(target=_send, daemon=True).start()",
    "_MAIL_POOL.submit(_send)",
    1,
)
text = text.replace(
    "mail = Mail(app)",
    "mail = Mail(app)\nfrom concurrent.futures import ThreadPoolExecutor\n_MAIL_POOL = ThreadPoolExecutor(max_workers=2)",
    1,
)

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(text)
print('Patched', path)
