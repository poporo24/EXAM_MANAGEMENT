import mysql.connector

try:
    db = mysql.connector.connect(
        host='mysql-5807518-johnpaulbaltazar2401-f645.i.aivencloud.com',
        user='avnadmin',
        password='AVNS_0uijwdmnhsiqSaQyce-',
        database='defaultdb',
        port=15268
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, email, role, is_active FROM users")
    users = cursor.fetchall()
    for u in users:
        print(u)
    db.close()
except Exception as e:
    print(f"Error: {e}")
