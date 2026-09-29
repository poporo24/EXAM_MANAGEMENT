import mysql.connector

conn = mysql.connector.connect(
    host="143.244.131.15",
    user="avnadmin",
    password="AVNS_0uijwdmnhsiqSaQyce-",
    database="defaultdb",
    port=15268
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, email, role, is_super_admin, full_name FROM users WHERE email='superadmin@cca.edu.ph'")
print(cursor.fetchone())
conn.close()
