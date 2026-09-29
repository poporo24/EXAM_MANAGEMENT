import os
import re

filepath = 'system/database.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Look for the open_db function
new_open_db = '''
def open_db():
    import os
    import mysql.connector
    
    # Check if we are on Render (using Aiven remote DB)
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # Connect using the remote URL (mysql://user:pass@host:port/dbname)
        import urllib.parse
        url = urllib.parse.urlparse(db_url)
        try:
            return mysql.connector.connect(
                host=url.hostname,
                user=url.username,
                password=url.password,
                database=url.path[1:], # remove leading slash
                port=url.port or 3306
            )
        except mysql.connector.Error as err:
            print(f"Remote DB Error: {err}")
            return None
    else:
        # Local XAMPP connection
        try:
            return mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="cca_exam_management_db"
            )
        except mysql.connector.Error as err:
            print(f"Local DB Error: {err}")
            return None
'''

content = re.sub(r'def open_db\(\):.*?(?=def |$)', new_open_db.strip() + '\n\n', content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated database.py to support remote connections")
