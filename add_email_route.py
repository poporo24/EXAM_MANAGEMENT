import re

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

new_route = '''
@app.route("/super_admin/update_email", methods=["POST"])
def super_update_email():
    if not session.get('is_super_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))
    
    new_email = request.form.get("new_email", "").strip()
    if not new_email.endswith("@cca.edu.ph"):
        flash("Email must be a valid @cca.edu.ph address.", "danger")
        return redirect(url_for('super_admin_page'))
        
    user_id = session.get('user_id')
    db = open_db()
    if db:
        try:
            c = db.cursor(dictionary=True)
            # Check if email is already used by someone else
            c.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, user_id))
            if c.fetchone():
                flash("That email is already in use.", "danger")
                return redirect(url_for('super_admin_page'))
                
            # Get current email to find Firebase user
            c.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            current_user = c.fetchone()
            
            if current_user:
                # 1. Update Firebase
                from firebase_admin import auth as fb_auth
                try:
                    fb_user = fb_auth.get_user_by_email(current_user['email'])
                    fb_auth.update_user(fb_user.uid, email=new_email)
                except fb_auth.UserNotFoundError:
                    # If not in firebase for some reason, create them? Or skip.
                    pass
                except Exception as fb_err:
                    flash(f"Cloud Sync Error: {fb_err}", "danger")
                    return redirect(url_for('super_admin_page'))
                
                # 2. Update Local DB
                c.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
                db.commit()
                flash("Superadmin email has been successfully updated! Password resets will now go to this new address.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return redirect(url_for('super_admin_page'))
'''

if 'def super_update_email' not in app_content:
    app_content = app_content.replace('@app.route("/super_admin/delete_user', new_route + '\n@app.route("/super_admin/delete_user')
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("Added update_email route to app.py")
