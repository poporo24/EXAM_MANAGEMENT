with open("template/super_admin.html", "r", encoding="utf-8") as f:
    html = f.read()

bad_tag = '<script src="https://cdn.tailwindcss.com">\n          \n          function showEditConfirmation()'
good_tag = '<script src="https://cdn.tailwindcss.com"></script>\n    <script>\n          function showEditConfirmation()'

if bad_tag in html:
    html = html.replace(bad_tag, good_tag)
    with open("template/super_admin.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Fixed script tag in super_admin.html")
else:
    print("Could not find bad tag")
