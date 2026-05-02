import mysql.connector

def create_instructor_table():
    try:
        print("Connecting to database222...")
        # Connect exactly like your main app does
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
            database="database222" 
        )
        cursor = db.cursor()
        
        # The SQL command to create the table
        sql_query = """
        CREATE TABLE IF NOT EXISTS instructors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            department VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'Active'
        );
        """
        
        cursor.execute(sql_query)
        print("✅ SUCCESS! The 'instructors' table has been added to your database.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    create_instructor_table()