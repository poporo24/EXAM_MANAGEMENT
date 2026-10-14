with open("system/database.py", "r", encoding="utf-8") as f:
    db = f.read()

bad_return = """        return {
            'rooms': [{'id': r['id'], 'name': f"{r['name']} (Cap: {r['capacity']})"} for r in all_rooms if r['id'] not in busy_rooms],
            'instructors': [{'id': i['id'], 'name': i['name']} for i in all_insts]
        }"""

good_return = """        return {
            'rooms': [{'id': r['id'], 'name': f"{r['name']} (Cap: {r['capacity']})"} for r in all_rooms if r['id'] not in busy_rooms],
            'instructors': valid_insts
        }"""

if bad_return in db:
    db = db.replace(bad_return, good_return)
    with open("system/database.py", "w", encoding="utf-8") as f:
        f.write(db)
    print("Fixed get_available_resources")
else:
    print("Could not find bad return")
