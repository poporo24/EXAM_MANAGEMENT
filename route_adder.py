import re

with open('app.py', 'r', encoding='utf-8') as f:
    data = f.read()

old_code = r'''@app\.route\("/register", methods=\["GET"\]\)
def register_page\(\):'''

new_code = '''@app.route("/terms")
def terms_page():
    return render_template("terms.html")

@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

@app.route("/register", methods=["GET"])
def register_page():'''

data = re.sub(old_code, new_code, data)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(data)
