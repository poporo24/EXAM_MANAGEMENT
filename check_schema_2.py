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
columns = [row['Field'] for row in cursor.fetchall()]
print(columns)
conn.close()
