import mysql.connector

try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="exam_management"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, email, role, is_active FROM users WHERE role='admin' OR role='secretary'")
    admins = cursor.fetchall()
    for a in admins:
        print(a)
    db.close()
except Exception as e:
    print(f"Error: {e}")
