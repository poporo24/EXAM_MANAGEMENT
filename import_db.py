import pymysql

conn = pymysql.connect(
    host="143.244.131.15",
    user="avnadmin",
    password="AVNS_0uijwdmnhsiqSaQyce-",
    database="defaultdb",
    port=15268,
    client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
)
cursor = conn.cursor()

try:
    with open('cca_exam_db_export.sql', 'r', encoding='utf-16') as f:
        sql_script = f.read()
except UnicodeDecodeError:
    with open('cca_exam_db_export.sql', 'r', encoding='utf-8', errors='ignore') as f:
        sql_script = f.read()

cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
cursor.execute(sql_script)
cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
conn.commit()
conn.close()
print("Import complete!")
