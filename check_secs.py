import mysql.connector

conn = mysql.connector.connect(
    host="143.244.131.15",
    user="avnadmin",
    password="AVNS_0uijwdmnhsiqSaQyce-",
    database="defaultdb",
    port=15268
)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT section FROM users WHERE section IS NOT NULL AND section != ''")
users_sec = cursor.fetchall()
print("Users table sections:", users_sec)

cursor.execute("SELECT DISTINCT section FROM exams WHERE section IS NOT NULL AND section != ''")
exams_sec = cursor.fetchall()
print("Exams table sections:", exams_sec)

conn.close()
