import mysql.connector

conn = mysql.connector.connect(
    host="143.244.131.15",
    user="avnadmin",
    password="AVNS_0uijwdmnhsiqSaQyce-",
    database="defaultdb",
    port=15268
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, email, role FROM users LIMIT 5;")
for row in cursor.fetchall():
    print(row)
conn.close()
