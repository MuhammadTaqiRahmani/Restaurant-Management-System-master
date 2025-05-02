import sqlite3
import os

DB_PATH = "restaurant.db"

def check_employee_table():
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} does not exist!")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%employee%';")
    tables = cursor.fetchall()
    
    print(f"Employee-related tables found: {tables}")
    
    # Check both possible table names
    for table_name in ['employeesTestDine', 'employeeTestDine']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Table '{table_name}' exists with {count} records")
            
            # Show schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"Table schema for '{table_name}':")
            for col in columns:
                print(f"  {col}")
                
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print(f"Sample data from '{table_name}':")
            for row in rows:
                print(f"  {row}")
            
        except sqlite3.OperationalError as e:
            print(f"Error checking table '{table_name}': {e}")
    
    conn.close()

if __name__ == "__main__":
    check_employee_table()