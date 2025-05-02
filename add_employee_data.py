import sqlite3
import os

DB_PATH = "restaurant.db"

def add_employee_data():
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} does not exist!")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # First, let's make sure we have the necessary roles
    print("Checking role data...")
    cursor.execute("SELECT COUNT(*) FROM rolesTestDine")
    roles_count = cursor.fetchone()[0]
    
    if roles_count == 0:
        print("Adding default roles...")
        roles = [
            ('Waiter',),
            ('Chef',),
            ('Manager',),
            ('Cashier',),
            ('Kitchen',)
        ]
        cursor.executemany("INSERT INTO rolesTestDine (role) VALUES (?)", roles)
        print("Default roles added successfully")
    
    # Check existing employees
    cursor.execute("SELECT COUNT(*) FROM employeesTestDine")
    employee_count = cursor.fetchone()[0]
    print(f"Current employee count: {employee_count}")
    
    # Get the schema information to use the correct column names
    cursor.execute("PRAGMA table_info(employeesTestDine)")
    columns = cursor.fetchall()
    print("Table schema:")
    column_names = [col[1] for col in columns]
    print(f"Column names: {column_names}")
    
    # Add employee data for Ali yosuf with ID 1002
    # Note: SQLite will auto-increment IDs, so we need to make sure our ID will be 1002
    
    # Get the current max ID
    cursor.execute("SELECT MAX(s_no) FROM employeesTestDine")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    
    print(f"Current max employee ID: {max_id}")
    
    if max_id < 1002:
        # Adjust the SQLite sequence
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='employeesTestDine'")
        cursor.execute("INSERT INTO sqlite_sequence VALUES ('employeesTestDine', 1001)")
        
    # Check if the employee already exists
    cursor.execute("SELECT * FROM employeesTestDine WHERE s_no = 1002")
    if not cursor.fetchone():
        # Get role ID for the employee role (assuming a role like 'Waiter' for Ali)
        cursor.execute("SELECT s_no FROM rolesTestDine WHERE role = 'Waiter'")
        role_id = cursor.fetchone()[0]
        
        # Add Ali yosuf as employee ID 1002
        # Using the correct column names based on schema
        name_col = 'name'  # The column name for employee name
        role_col = 'e_role'  # The column name for employee role
        
        print(f"Adding Ali yosuf as employee ID 1002 using columns {name_col} and {role_col}...")
        
        cursor.execute(
            f"INSERT INTO employeesTestDine (s_no, {name_col}, {role_col}) VALUES (?, ?, ?)",
            (1002, "Ali yosuf", role_id)
        )
        print("Employee Ali yosuf added successfully")
    else:
        print("Employee with ID 1002 already exists")
    
    # Verify the employee was added
    cursor.execute("SELECT * FROM employeesTestDine WHERE s_no = 1002")
    employee = cursor.fetchone()
    print(f"Employee with ID 1002: {employee}")
    
    # Check the total employee count after adding
    cursor.execute("SELECT COUNT(*) FROM employeesTestDine")
    employee_count_after = cursor.fetchone()[0]
    print(f"Updated employee count: {employee_count_after}")
    
    # Check if there's a user associated with this employee ID
    cursor.execute("SELECT * FROM users WHERE employee_id = 1002")
    user = cursor.fetchone()
    print(f"User associated with employee ID 1002: {user}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    print("Database updated successfully")

if __name__ == "__main__":
    add_employee_data()