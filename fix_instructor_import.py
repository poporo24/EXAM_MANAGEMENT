"""
fix_instructor_import.py
------------------------
Fixes the case where instructor CSV rows were mistakenly imported into the
'subjects' table instead of the 'instructors' table.

Run this script from the EXAM_MANAGEMENT directory:
    python fix_instructor_import.py

What it does:
  1. Scans the subjects table for rows that look like instructor entries
     (i.e. rows whose 'name' column matches instructor names from the
     template_instructors.csv, OR all subjects that were inserted after
     a given timestamp if you know when the bad import happened).
  2. Asks you to confirm before deleting.
  3. Adds the data correctly to the instructors table via add_instructor().

Edit INSTRUCTOR_NAMES below if you used a different CSV.
"""

import sys
import mysql.connector

# ── Config ────────────────────────────────────────────────────────────────────
DB = dict(host="localhost", user="root", password="", database="cca_exam_management_db")

# Paste the names from the CSV that were wrongly imported as subjects.
# Leave this empty ([]) to interactively list ALL subjects and pick.
INSTRUCTOR_NAMES = [
    "Clark Soysoy",
    "Izzy Padoc",
    "Kurt Salonga",
    "Maria Santos",
    "JM Kagrab",
    "Jergie Toti",
    "Ana Reyes",
    "Carlo Dizon",
    "Sofia Lim",
    "Rafael Cruz",
    "Linda Mendoza",
]

# Instructor details matching each name above (from template_instructors.csv)
# Format: name -> {institute_code, building, is_pwd, subjects_taught}
INSTRUCTOR_DATA = {
    "Clark Soysoy":  dict(institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="IT 2|Database Management"),
    "Izzy Padoc":    dict(institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Web Development|System Analysis"),
    "Kurt Salonga":  dict(institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Computer Networks|Operating Systems"),
    "Maria Santos":  dict(institute_code="ICSLIS", building="Main Building", is_pwd=1, subjects_taught="Programming 1|Programming 2"),
    "JM Kagrab":     dict(institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Information Management|Database"),
    "Jergie Toti":   dict(institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Library Science|Research Methods"),
    "Ana Reyes":     dict(institute_code="IBM",    building="Business Hall",  is_pwd=0, subjects_taught="Business Management|Marketing"),
    "Carlo Dizon":   dict(institute_code="IBM",    building="Business Hall",  is_pwd=0, subjects_taught="Accounting|Business Law"),
    "Sofia Lim":     dict(institute_code="IBM",    building="Business Hall",  is_pwd=1, subjects_taught="Economics|Finance"),
    "Rafael Cruz":   dict(institute_code="IEAS",   building="Education Hall", is_pwd=0, subjects_taught="Filipino|Arts"),
    "Linda Mendoza": dict(institute_code="IEAS",   building="Education Hall", is_pwd=0, subjects_taught="Education|Child Psychology"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_conn():
    return mysql.connector.connect(**DB)

def list_bad_subjects(cursor, names):
    if names:
        fmt = ",".join(["%s"] * len(names))
        cursor.execute(f"SELECT id, name, code FROM subjects WHERE name IN ({fmt})", tuple(names))
    else:
        cursor.execute("SELECT id, name, code FROM subjects ORDER BY id DESC LIMIT 50")
    return cursor.fetchall()

def resolve_institute_id(cursor, code):
    cursor.execute("SELECT id FROM institutes WHERE code=%s", (code,))
    row = cursor.fetchone()
    return row[0] if row else None

def instructor_exists(cursor, name):
    cursor.execute("SELECT id FROM instructors WHERE name=%s", (name,))
    return cursor.fetchone() is not None

def add_instructor_row(cursor, name, data, institute_id):
    from system.logic import hash_password
    cursor.execute(
        "INSERT INTO instructors (name, status, institute_id, building, is_pwd, subjects_taught) "
        "VALUES (%s, 'Active', %s, %s, %s, %s)",
        (name, institute_id, data['building'], data['is_pwd'], data['subjects_taught'])
    )
    instructor_id = cursor.lastrowid
    email_name = name.lower().replace(" ", ".")
    proctor_email = f"{email_name}@cca.edu.ph"
    cursor.execute("SELECT id FROM users WHERE email=%s", (proctor_email,))
    if cursor.fetchone():
        proctor_email = f"{email_name}.{instructor_id}@cca.edu.ph"
    hashed = hash_password("proctor123")
    cursor.execute(
        "INSERT INTO users (full_name, email, password, role, instructor_id) VALUES (%s, %s, %s, 'proctor', %s)",
        (name, proctor_email, hashed, instructor_id)
    )
    return instructor_id, proctor_email

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    conn = get_conn()
    if not conn:
        print("❌ Could not connect to database.")
        sys.exit(1)

    cursor = conn.cursor()

    print("\n=== Step 1: Finding wrongly-imported subjects ===")
    bad_rows = list_bad_subjects(cursor, INSTRUCTOR_NAMES)

    if not bad_rows:
        print("✅ No matching rows found in subjects table. Nothing to fix!")
        conn.close()
        return

    print(f"\nFound {len(bad_rows)} subject row(s) that appear to be instructor data:\n")
    for row in bad_rows:
        print(f"  [Subject ID {row[0]}] name='{row[1]}', code='{row[2]}'")

    confirm = input("\nDelete these from 'subjects' and re-add as instructors? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Aborted. No changes made.")
        conn.close()
        return

    print("\n=== Step 2: Deleting bad subject rows ===")
    ids_to_delete = [r[0] for r in bad_rows]
    fmt = ",".join(["%s"] * len(ids_to_delete))
    cursor.execute(f"DELETE FROM subjects WHERE id IN ({fmt})", tuple(ids_to_delete))
    conn.commit()
    print(f"  ✅ Deleted {cursor.rowcount} row(s) from subjects.")

    print("\n=== Step 3: Adding as instructors ===")
    added, skipped = 0, 0
    for row in bad_rows:
        name = row[1]
        data = INSTRUCTOR_DATA.get(name)
        if not data:
            print(f"  ⚠️  No instructor data configured for '{name}' — skipping.")
            skipped += 1
            continue
        if instructor_exists(cursor, name):
            print(f"  ⚠️  Instructor '{name}' already exists — skipping.")
            skipped += 1
            continue
        inst_id = resolve_institute_id(cursor, data['institute_code'])
        try:
            instr_id, email = add_instructor_row(cursor, name, data, inst_id)
            conn.commit()
            print(f"  ✅ Added instructor '{name}' (ID {instr_id}, login: {email})")
            added += 1
        except Exception as e:
            print(f"  ❌ Failed to add '{name}': {e}")
            conn.rollback()

    print(f"\n=== Done! {added} instructor(s) added, {skipped} skipped. ===\n")
    conn.close()

if __name__ == "__main__":
    main()
