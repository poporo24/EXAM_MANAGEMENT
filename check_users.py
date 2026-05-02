from system.database import open_db

db = open_db()
c = db.cursor()

print("=== USERS TABLE ===")
c.execute("SHOW COLUMNS FROM users")
for col in c.fetchall():
    print(col)

print("\n=== SAMPLE USERS ===")
c.execute("SELECT * FROM users LIMIT 10")
for r in c.fetchall():
    print(r)

db.close()
