with open("app.py", "r", encoding="utf-8") as f:
    app = f.read()

bad_block = """
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
    return redirect(url_for('super_admin_page'))
"""

if bad_block in app:
    app = app.replace(bad_block, "")
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app)
    print("Fixed bad block")
else:
    print("Could not find bad block exactly")
