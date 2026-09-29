"""
init_db.py  - Full database initializer for the CCA Exam Management System
Run once:   python init_db.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from system.database import open_db

db = open_db()
if not db:
    print("ERROR: Could not connect to MySQL. Make sure MySQL/XAMPP is running.")
    exit(1)

c = db.cursor()

print("=== Creating tables ===\n")

# 1. rooms
c.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(100) NOT NULL,
    capacity  INT NOT NULL DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("[OK] rooms")

# 2. instructors
c.execute("""
CREATE TABLE IF NOT EXISTS instructors (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    status     ENUM('Active','Inactive') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("[OK] instructors")

# 3. users  (admin / proctor / student)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(150) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'student',
    instructor_id INT          NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("[OK] users")

# 4. exams
c.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    subject_name     VARCHAR(150) NOT NULL,
    section          VARCHAR(50)  NULL,
    subject_type     ENUM('Major','Minor') NOT NULL DEFAULT 'Major',
    duration_minutes INT          NOT NULL DEFAULT 60,
    exam_date_time   DATETIME     NULL,
    room_id          INT          NULL,
    instructor_id    INT          NULL,
    instructor_name  VARCHAR(100) NULL,
    status           ENUM('Pending','Scheduled','Unscheduled') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (room_id)       REFERENCES rooms(id)       ON DELETE SET NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("[OK] exams")

# 5. proctor_availability
c.execute("""
CREATE TABLE IF NOT EXISTS proctor_availability (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id  INT  NOT NULL,
    available_date DATE NOT NULL,
    start_time     TIME NOT NULL DEFAULT '07:00:00',
    end_time       TIME NOT NULL DEFAULT '20:00:00',
    UNIQUE KEY uq_proctor_date (instructor_id, available_date),
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("[OK] proctor_availability")

db.commit()

# -- Seed admin account -------------------------------------------------------
print("\n=== Seeding admin account ===")
c.execute("SELECT id FROM users WHERE email = 'admin@cca.edu.ph'")
if c.fetchone():
    print("   Admin already exists -- skipped.")
else:
    c.execute(
        "INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, 'admin')",
        ("CCA Admin", "admin@cca.edu.ph", "admin123")
    )
    db.commit()
    print("   [OK] admin@cca.edu.ph  /  admin123")

# -- Summary ------------------------------------------------------------------
print("\n=== Tables in cca_exam_management_db ===")
c.execute("SHOW TABLES")
for (tbl,) in c.fetchall():
    print(f"   - {tbl}")

db.close()
print("\n[DONE] Database fully initialized. Run the app with:  python app.py")
