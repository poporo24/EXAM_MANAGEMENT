import mysql.connector
db = mysql.connector.connect(host='localhost', user='root', password='', database='cca_exam_management_db')
c = db.cursor()
c.execute("SELECT status, COUNT(*) as cnt FROM exams GROUP BY status")
for row in c.fetchall():
    print(row)
db.close()
