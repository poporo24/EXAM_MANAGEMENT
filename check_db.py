import mysql.connector
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="cca_exam_management_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE role IN ('admin', 'super_admin')")
    users = cursor.fetchall()
    for u in users:
        print(u['email'], u['role'])
    db.close()
except Exception as e:
    print(f"Error: {e}")
