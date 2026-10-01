import re

with open("app.py", "r", encoding="utf-8") as f:
    app = f.read()

# We need to replace super_edit_user
new_func = r"""@app.route("/super_admin/edit_user/<int:id>", methods=["POST"])
def super_edit_user(id):
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    try:
        # Construct full name from 4 fields if they exist, otherwise fallback to "name"
        last = request.form.get("last_name", "").strip()
        first = request.form.get("first_name", "").strip()
        middle = request.form.get("middle_name", "").strip()
        suffix = request.form.get("suffix", "").strip()
        
        if last and first:
            # Format: Lastname, Firstname M. Suffix
            full_name = f"{last}, {first}"
            if middle:
                full_name += f" {middle[0]}." if len(middle) == 1 else f" {middle}"
            if suffix:
                full_name += f" {suffix}"
        else:
            full_name = request.form.get("name", "").strip()
            
        email        = request.form.get("email", "").strip()
        role         = request.form.get("role", "student").strip()
        section      = request.form.get("section", "").strip()
        institute_id = request.form.get("institute_id") or None
        is_sa        = 1 if request.form.get("is_super_admin") else 0

        # Validate role
        if role not in ("admin", "secretary", "proctor", "student"):
            flash("Invalid role selected.", "danger")
            return redirect(url_for('super_admin_page'))

        # GET OLD EMAIL FIRST before updating DB!
        from system.database import open_db, update_user
        db = open_db()
        old_email = None
        if db:
            try:
                c = db.cursor(dictionary=True)
                c.execute("SELECT email FROM users WHERE id = %s", (id,))
                row = c.fetchone()
                if row: old_email = row['email']
            finally:
                db.close()

        # Update local DB
        update_user(id, full_name, email, role, section, institute_id, is_sa)

        # Sync email & name to Firebase
        if old_email:
            try:
                from firebase_admin import auth as fb_auth
                try:
                    fb_user = fb_auth.get_user_by_email(old_email)
                    # Update both email and display_name
                    fb_auth.update_user(fb_user.uid, email=email, display_name=full_name)
                except fb_auth.UserNotFoundError:
                    # If they don't exist in Firebase, maybe create them?
                    pass
            except Exception as fb_err:
                print(f"Firebase sync error: {fb_err}")

        flash(f"User '{full_name}' updated successfully to role '{role}'.", "success")
    except Exception as e:
        flash(f"Error updating user: {str(e)}", "danger")
    return redirect(url_for('super_admin_page'))"""

# We'll use regex to replace it
app = re.sub(r'@app\.route\("/super_admin/edit_user/<int:id>".*?return redirect\(url_for\(\'super_admin_page\'\)\)', new_func, app, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app)
print("Patched edit user in app.py")
