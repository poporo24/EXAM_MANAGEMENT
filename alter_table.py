import mysql.connector
conn = mysql.connector.connect(
    host='143.244.131.15',
    user='avnadmin',
    password='AVNS_0uijwdmnhsiqSaQyce-',
    database='defaultdb',
    port=15268
)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE system_settings ADD COLUMN major_duration_hrs FLOAT DEFAULT 2.0")
    print("Added major_duration_hrs")
except Exception as e:
    print(e)
    
try:
    cursor.execute("ALTER TABLE system_settings ADD COLUMN minor_duration_hrs FLOAT DEFAULT 1.0")
    print("Added minor_duration_hrs")
except Exception as e:
    print(e)

conn.commit()
conn.close()
