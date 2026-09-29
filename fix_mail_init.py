app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_config = '''def _configure_mail():
    try:
        s = get_system_settings()
    except Exception:
        s = {}
    app.config['MAIL_SERVER']         = s.get('smtp_host', '') or ''
    app.config['MAIL_PORT']           = int(s.get('smtp_port') or 587)
    app.config['MAIL_USERNAME']       = s.get('smtp_user', '') or ''
    app.config['MAIL_PASSWORD']       = s.get('smtp_password', '') or ''
    app.config['MAIL_DEFAULT_SENDER'] = s.get('smtp_from', '') or ''
    app.config['MAIL_USE_TLS']        = bool(s.get('smtp_use_tls', 1))
    app.config['MAIL_USE_SSL']        = False
    app.config['MAIL_SUPPRESS_SEND']  = not bool(app.config['MAIL_SERVER'])'''

new_config = '''def _configure_mail():
    try:
        s = get_system_settings()
    except Exception:
        s = {}
    app.config['MAIL_SERVER']         = s.get('smtp_host', '') or ''
    app.config['MAIL_PORT']           = int(s.get('smtp_port') or 587)
    app.config['MAIL_USERNAME']       = s.get('smtp_user', '') or ''
    app.config['MAIL_PASSWORD']       = s.get('smtp_password', '') or ''
    app.config['MAIL_DEFAULT_SENDER'] = s.get('smtp_from', '') or ''
    app.config['MAIL_USE_TLS']        = bool(s.get('smtp_use_tls', 1))
    app.config['MAIL_USE_SSL']        = False
    app.config['MAIL_SUPPRESS_SEND']  = not bool(app.config['MAIL_SERVER'])
    
    # Re-initialize the Mail extension to pick up these new config values immediately
    if hasattr(app, 'extensions') and 'mail' in app.extensions:
        mail.init_app(app)'''

if old_config in content:
    content = content.replace(old_config, new_config)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed _configure_mail!")
else:
    print("Could not find _configure_mail exact match.")
