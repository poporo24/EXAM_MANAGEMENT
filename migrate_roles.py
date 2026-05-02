from system.database import open_db

db = open_db()
c = db.cursor()

print("=== Step 1: Add instructor_id FK to users ===")
# Check if column already exists
c.execute("SHOW COLUMNS FROM users LIKE 'instructor_id'")
if c.fetchone():
    print("instructor_id column already exists, skipping.")
else:
    c.execute("ALTER TABLE users ADD COLUMN instructor_id INT NULL")
    db.commit()
    print("Added instructor_id column to users.")

print("\n=== Step 2: Ensure 'proctor' is a valid role ===")
# role is varchar(20), so no ENUM change needed — already accepts 'proctor'
print("role column is VARCHAR, no migration needed.")

print("\n=== Step 3: Seed a demo proctor account for each instructor ===")
# Get all instructors
c.execute("SELECT id, name FROM instructors")
instructors = c.fetchall()
print(f"Found {len(instructors)} instructors.")

for inst_id, inst_name in instructors:
    # Check if a proctor user already exists for this instructor
    c.execute("SELECT id FROM users WHERE instructor_id = %s AND role = 'proctor'", (inst_id,))
    if c.fetchone():
        print(f"  Proctor account for [{inst_id}] {inst_name} already exists, skipping.")
        continue

    # Create email from name: "Clark Soysoy" -> "clark.soysoy@cca.edu.ph"
    email_name = inst_name.lower().replace(" ", ".")
    email = f"{email_name}@cca.edu.ph"
    password = "proctor123"

    c.execute(
        "INSERT INTO users (full_name, email, password, role, instructor_id) VALUES (%s, %s, %s, 'proctor', %s)",
        (inst_name, email, password, inst_id)
    )
    print(f"  Created proctor: {email} / {password} -> Instructor [{inst_id}] {inst_name}")

db.commit()

print("\n=== Final Users Table ===")
c.execute("SELECT id, full_name, email, role, instructor_id FROM users ORDER BY role, id")
for r in c.fetchall():
    print(r)

db.close()
print("\nMigration complete!")
