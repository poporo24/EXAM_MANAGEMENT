"""
add_instructors_fix.py
-----------------------
Adds the instructor rows that were previously wrongly imported as subjects.
Run from the EXAM_MANAGEMENT directory:  python add_instructors_fix.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')  # force UTF-8 output

import mysql.connector
from system.logic import hash_password

DB = dict(host="localhost", user="root", password="", database="cca_exam_management_db")

INSTRUCTORS = [
    dict(name="Clark Soysoy",  department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="IT 2|Database Management"),
    dict(name="Izzy Padoc",    department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Web Development|System Analysis"),
    dict(name="Kurt Salonga",  department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Computer Networks|Operating Systems"),
    dict(name="Maria Santos",  department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=1, subjects_taught="Programming 1|Programming 2"),
    dict(name="JM Kagrab",     department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Information Management|Database"),
    dict(name="Jergie Toti",   department="ICSLIS", institute_code="ICSLIS", building="Main Building", is_pwd=0, subjects_taught="Library Science|Research Methods"),
    dict(name="Ana Reyes",     department="IBM",    institute_code="IBM",    building="Business Hall",  is_pwd=0, subjects_taught="Business Management|Marketing"),
    dict(name="Carlo Dizon",   department="IBM",    institute_code="IBM",    building="Business Hall",  is_pwd=0, subjects_taught="Accounting|Business Law"),
    dict(name="Sofia Lim",     department="IBM",    institute_code="IBM",    building="Business Hall",  is_pwd=1, subjects_taught="Economics|Finance"),
    dict(name="Rafael Cruz",   department="IEAS",   institute_code="IEAS",   building="Education Hall", is_pwd=0, subjects_taught="Filipino|Arts"),
    dict(name="Linda Mendoza", department="IEAS",   institute_code="IEAS",   building="Education Hall", is_pwd=0, subjects_taught="Education|Child Psychology"),
]

def main():
    conn = mysql.connector.connect(**DB)
    cursor = conn.cursor()
    added, skipped = 0, 0

    for d in INSTRUCTORS:
        name = d['name']
        # Check if already exists
        cursor.execute("SELECT id FROM instructors WHERE name=%s", (name,))
        if cursor.fetchone():
            print(f"  SKIP: '{name}' already exists as instructor.")
            skipped += 1
            continue

        # Resolve institute_id
        cursor.execute("SELECT id FROM institutes WHERE code=%s", (d['institute_code'],))
        row = cursor.fetchone()
        institute_id = row[0] if row else None

        # Insert instructor
        cursor.execute(
            "INSERT INTO instructors (name, department, status, institute_id, building, is_pwd, subjects_taught) "
            "VALUES (%s, %s, 'Active', %s, %s, %s, %s)",
            (name, d['department'], institute_id, d['building'], d['is_pwd'], d['subjects_taught'])
        )
        instructor_id = cursor.lastrowid

        # Create proctor login
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
        conn.commit()
        print(f"  ADDED: '{name}' (ID {instructor_id}, login: {proctor_email})")
        added += 1

    conn.close()
    print(f"\nDone! {added} instructor(s) added, {skipped} skipped.")

if __name__ == "__main__":
    main()
