"""
migrate_full.py — Full migration for CCA Exam Management v2
Run once:  python migrate_full.py
Safe to re-run (uses IF NOT EXISTS / IF EXISTS guards).
"""
import sys
import bcrypt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from system.database import open_db

db = open_db()
if not db:
    print("ERROR: Cannot connect to MySQL. Ensure XAMPP MySQL is running.")
    sys.exit(1)

c = db.cursor()
print("=" * 60)
print("CCA Exam Management — Full Database Migration v2")
print("=" * 60)

# ── 1. INSTITUTES ────────────────────────────────────────────────────────────
print("\n[1] institutes table...")
c.execute("""
CREATE TABLE IF NOT EXISTS institutes (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    code             VARCHAR(20)  NOT NULL UNIQUE,
    capacity_default INT          NOT NULL DEFAULT 50
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] institutes")

# ── 2. SUBJECTS (standalone) ─────────────────────────────────────────────────
print("\n[2] subjects table...")
c.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(150) NOT NULL,
    code             VARCHAR(50)  NULL,
    institute_id     INT          NULL,
    is_common        TINYINT(1)   NOT NULL DEFAULT 0,
    content_group_id INT          NULL,
    FOREIGN KEY (institute_id) REFERENCES institutes(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] subjects")

# ── 3. SYSTEM SETTINGS ────────────────────────────────────────────────────────
print("\n[3] system_settings table...")
c.execute("""
CREATE TABLE IF NOT EXISTS system_settings (
    id                          INT PRIMARY KEY DEFAULT 1,
    day_start                   TIME NOT NULL DEFAULT '07:00:00',
    day_end                     TIME NOT NULL DEFAULT '20:00:00',
    slot_interval_min           INT  NOT NULL DEFAULT 60,
    max_consecutive_proctor_hrs INT  NOT NULL DEFAULT 3,
    travel_buffer_min           INT  NOT NULL DEFAULT 15,
    smtp_host                   VARCHAR(150) DEFAULT '',
    smtp_port                   INT          DEFAULT 587,
    smtp_user                   VARCHAR(150) DEFAULT '',
    smtp_password               VARCHAR(255) DEFAULT '',
    smtp_from                   VARCHAR(150) DEFAULT '',
    smtp_use_tls                TINYINT(1)   DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
# Seed default row
c.execute("SELECT id FROM system_settings WHERE id = 1")
if not c.fetchone():
    c.execute("""
        INSERT INTO system_settings (id, day_start, day_end, slot_interval_min,
            max_consecutive_proctor_hrs, travel_buffer_min)
        VALUES (1, '07:00:00', '20:00:00', 60, 3, 15)
    """)
    print("   [OK] system_settings (seeded defaults)")
else:
    print("   [OK] system_settings (already exists)")

# ── 4. RELIEVERS ──────────────────────────────────────────────────────────────
print("\n[4] relievers table...")
c.execute("""
CREATE TABLE IF NOT EXISTS relievers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    exam_id       INT NOT NULL,
    instructor_id INT NOT NULL,
    reason        TEXT NULL,
    assigned_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id)       REFERENCES exams(id)       ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] relievers")

# ── 5. EXAM COLLECTION (secretary) ──────────────────────────────────────────
print("\n[5] exam_collection table...")
c.execute("""
CREATE TABLE IF NOT EXISTS exam_collection (
    id                        INT AUTO_INCREMENT PRIMARY KEY,
    exam_id                   INT  NOT NULL,
    collected_by_instructor_id INT NULL,
    collected_at              DATETIME NULL,
    returned_at               DATETIME NULL,
    notes                     TEXT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by_instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] exam_collection")

# ── 6. NOTIFICATIONS ──────────────────────────────────────────────────────────
print("\n[6] notifications table...")
c.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    title      VARCHAR(200) NOT NULL,
    message    TEXT         NOT NULL,
    is_read    TINYINT(1)   NOT NULL DEFAULT 0,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] notifications")

# ── 7. PROCTOR ABSENCE ────────────────────────────────────────────────────────
print("\n[7] proctor_absence table...")
c.execute("""
CREATE TABLE IF NOT EXISTS proctor_absence (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT  NOT NULL,
    exam_id       INT  NOT NULL,
    reason        TEXT NULL,
    reported_by   INT  NULL,
    reported_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id)       REFERENCES exams(id)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
print("   [OK] proctor_absence")

# ── 8. MODIFY EXISTING TABLES ────────────────────────────────────────────────
print("\n[8] Altering existing tables...")

def add_col(table, col, definition):
    try:
        c.execute(f"ALTER TABLE `{table}` ADD COLUMN {col} {definition}")
        print(f"   [+] {table}.{col}")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"   [~] {table}.{col} already exists — skipped")
        else:
            print(f"   [!] {table}.{col}: {e}")

# users
add_col("users", "section",       "VARCHAR(50) NULL")
add_col("users", "institute_id",  "INT NULL")
add_col("users", "is_super_admin","TINYINT(1) NOT NULL DEFAULT 0")

# instructors
add_col("instructors", "institute_id",    "INT NULL")
add_col("instructors", "building",        "VARCHAR(100) NULL")
add_col("instructors", "is_pwd",          "TINYINT(1) NOT NULL DEFAULT 0")
add_col("instructors", "subjects_taught", "TEXT NULL COMMENT 'comma-sep subject IDs'")

# rooms
add_col("rooms", "institute_id",     "INT NULL")
add_col("rooms", "building",         "VARCHAR(100) NULL")
add_col("rooms", "floor",            "INT NULL DEFAULT 1")
add_col("rooms", "is_pwd_accessible","TINYINT(1) NOT NULL DEFAULT 0")

# exams
add_col("exams", "institute_id", "INT NULL")
add_col("exams", "subject_id",   "INT NULL")

# exam_settings
add_col("exam_settings", "travel_buffer_min",       "INT NOT NULL DEFAULT 15")
add_col("exam_settings", "max_proctor_hours",        "INT NOT NULL DEFAULT 3")

# ── 9. SEED INSTITUTES ────────────────────────────────────────────────────────
print("\n[9] Seeding institutes...")
for code, name, cap in [("IEAS", "Institute of Education, Arts and Sciences", 50),
                         ("IBM",  "Institute of Business Management", 50),
                         ("ICSLIS", "Institute of Computer Science, Library and Information Science", 40)]:
    c.execute("SELECT id FROM institutes WHERE code = %s", (code,))
    if not c.fetchone():
        c.execute("INSERT INTO institutes (name, code, capacity_default) VALUES (%s, %s, %s)",
                  (name, code, cap))
        print(f"   [+] {code} — {name}")
    else:
        print(f"   [~] {code} already exists")

# ── 10. SEED SUPER ADMIN ─────────────────────────────────────────────────────
print("\n[10] Seeding super admin...")
c.execute("SELECT id FROM users WHERE email = 'superadmin@cca.edu.ph'")
if not c.fetchone():
    hashed = bcrypt.hashpw(b"superadmin123", bcrypt.gensalt()).decode()
    c.execute("""
        INSERT INTO users (full_name, email, password, role, is_super_admin)
        VALUES ('CCA Super Admin', 'superadmin@cca.edu.ph', %s, 'admin', 1)
    """, (hashed,))
    print("   [+] superadmin@cca.edu.ph / superadmin123")
else:
    print("   [~] Super admin already exists")

# ── 11. SEED SECRETARY ACCOUNT ───────────────────────────────────────────────
print("\n[11] Seeding secretary account...")
c.execute("SELECT id FROM users WHERE email = 'secretary@cca.edu.ph'")
if not c.fetchone():
    hashed = bcrypt.hashpw(b"secretary123", bcrypt.gensalt()).decode()
    c.execute("""
        INSERT INTO users (full_name, email, password, role)
        VALUES ('CCA Secretary', 'secretary@cca.edu.ph', %s, 'secretary')
    """, (hashed,))
    print("   [+] secretary@cca.edu.ph / secretary123")
else:
    print("   [~] Secretary already exists")

# ── 12. HASH EXISTING PLAIN-TEXT PASSWORDS ──────────────────────────────────
print("\n[12] Hashing plain-text passwords...")
c.execute("SELECT id, password FROM users")
rows = c.fetchall()
hashed_count = 0
for (uid, pwd) in rows:
    if pwd and not pwd.startswith("$2b$") and not pwd.startswith("$2a$"):
        new_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
        c.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, uid))
        hashed_count += 1
print(f"   [OK] Hashed {hashed_count} plain-text password(s)")

db.commit()
db.close()

print("\n" + "=" * 60)
print("[DONE] Migration complete.")
print("\nNew accounts:")
print("  Super Admin : superadmin@cca.edu.ph / superadmin123")
print("  Secretary   : secretary@cca.edu.ph  / secretary123")
print("  Admin       : admin@cca.edu.ph      / admin123  (re-hashed)")
print("=" * 60)
