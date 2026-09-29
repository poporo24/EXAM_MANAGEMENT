html_path = 'template/settings.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the input name from recipient_email to test_to to match app.py
if 'name="recipient_email"' in html:
    html = html.replace('name="recipient_email"', 'name="test_to"')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed test email form name!")
else:
    print("Already fixed or not found.")
