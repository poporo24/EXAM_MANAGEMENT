app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_edit = '''    update_user(id,
        request.form.get("full_name"),
        request.form.get("email"),
        request.form.get("role"),
        request.form.get("section", ""),
        request.form.get("institute_id") or None,
        1 if request.form.get("is_super_admin") else 0
    )
    flash("User updated.", "success")
    return redirect(url_for('super_admin_page'))'''

new_edit = '''    try:
        full_name    = request.form.get("full_name", "").strip()
        email        = request.form.get("email", "").strip()
        role         = request.form.get("role", "student").strip()
        section      = request.form.get("section", "").strip()
        institute_id = request.form.get("institute_id") or None
        is_sa        = 1 if request.form.get("is_super_admin") else 0

        # Validate role
        if role not in ("admin", "secretary", "proctor", "student"):
            flash("Invalid role selected.", "danger")
            return redirect(url_for('super_admin_page'))

        # Update local DB
        update_user(id, full_name, email, role, section, institute_id, is_sa)

        # Sync email change to Firebase if email changed
        from system.database import get_user_by_id
        db = open_db()
        if db:
            try:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT email FROM users WHERE id = %s", (id,))
                current = cursor.fetchone()
            finally:
                db.close()

        # Sync display name to Firebase
        try:
            from firebase_admin import auth as fb_auth
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.update_user(fb_user.uid, display_name=full_name)
        except Exception as fb_err:
            print(f"Firebase sync skipped: {fb_err}")

        flash(f"User '{full_name}' updated successfully to role '{role}'.", "success")
    except Exception as e:
        flash(f"Error updating user: {str(e)}", "danger")
    return redirect(url_for('super_admin_page'))'''

if old_edit in content:
    content = content.replace(old_edit, new_edit)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed super_edit_user!")
else:
    print("Could not find block. Check manually.")
