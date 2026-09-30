with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

old_code = """    # Try creating user in Firebase FIRST so we catch Firebase duplicates
    try:
        from firebase_admin import auth as fb_auth
        fb_auth.create_user(email=email, password=password, display_name=full_name)
    except fb_auth.EmailAlreadyExistsError:
        flash("That email is already registered in the cloud auth system.", "danger")
        return redirect(url_for('register_page'))
    except Exception as e:"""

new_code = """    # Try creating user in Firebase FIRST so we catch Firebase duplicates
    try:
        from firebase_admin import auth as fb_auth
        fb_auth.create_user(email=email, password=password, display_name=full_name)
    except fb_auth.EmailAlreadyExistsError:
        # User is in Firebase but not in MySQL (orphaned due to past rejection).
        # Safe to delete and recreate.
        try:
            fb_user = fb_auth.get_user_by_email(email)
            fb_auth.delete_user(fb_user.uid)
            fb_auth.create_user(email=email, password=password, display_name=full_name)
        except Exception as e:
            flash("That email is already registered in the cloud auth system.", "danger")
            return redirect(url_for('register_page'))
    except Exception as e:"""

if old_code in app_code:
    app_code = app_code.replace(old_code, new_code)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_code)
    print("Patched app.py")
else:
    print("Could not find the exact old_code")
