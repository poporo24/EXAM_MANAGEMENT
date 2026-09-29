import mysql.connector

conn = mysql.connector.connect(
    host="143.244.131.15",
    user="avnadmin",
    password="AVNS_0uijwdmnhsiqSaQyce-",
    database="defaultdb",
    port=15268
)
cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
for table in cursor.fetchall():
    print(table[0])
conn.close()
