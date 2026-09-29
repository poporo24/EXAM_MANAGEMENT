import mysql.connector
conn = mysql.connector.connect(
    host='143.244.131.15',
    user='avnadmin',
    password='AVNS_0uijwdmnhsiqSaQyce-',
    database='defaultdb',
    port=15268
)
cursor = conn.cursor(dictionary=True)
cursor.execute("DESCRIBE system_settings")
for row in cursor.fetchall():
    print(row['Field'])
conn.close()
