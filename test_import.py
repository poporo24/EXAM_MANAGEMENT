import system.database as db
from system.importer import parse_instructors_csv

csv_content = b"name,institute_code,email,availability\nJohn Doe,INST1,john@cca.edu.ph,\"Mon 07:00-12:00, Wed, Fri 13:00-17:00\""
rows, errors = parse_instructors_csv(csv_content)
print("Rows:", rows)
print("Errors:", errors)

if not errors:
    ok, import_errors = db.bulk_import_instructors(rows)
    print("Imported:", ok)
    print("Import errors:", import_errors)
