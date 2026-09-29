# Also verify the email exists in local DB 
import mysql.connector
conn = mysql.connector.connect(
    host='143.244.131.15',
    user='avnadmin',
    password='AVNS_0uijwdmnhsiqSaQyce-',
    database='defaultdb',
    port=15268
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, email, full_name, role, is_active, is_super_admin FROM users WHERE email = 'jpbaltazar23-0368@cca.edu.ph'")
row = cursor.fetchone()
print("DB Record:", row)

# Make sure it's active
if row:
    cursor.execute("UPDATE users SET is_active = 1 WHERE email = 'jpbaltazar23-0368@cca.edu.ph'")
    conn.commit()
    print("[FIXED] Account marked as active in DB")
conn.close()
