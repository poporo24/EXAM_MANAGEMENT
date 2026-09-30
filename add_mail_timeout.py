app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add a MAIL_TIMEOUT config
old_config = "app.config['MAIL_USE_SSL']        = False"
new_config = "app.config['MAIL_USE_SSL']        = False\n    app.config['MAIL_TIMEOUT']        = 5"
if old_config in content and "MAIL_TIMEOUT" not in content:
    content = content.replace(old_config, new_config)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added MAIL_TIMEOUT = 5")
else:
    print("Already added or not found.")
