from database import session_scope, engine
from models import User
from sqlalchemy import inspect, text
import os

def check_database_connection():
    """Check if the database connection is working and print connection details."""
    print("Checking database connection...")
    print(f"Connection string (without password): {str(engine.url).replace(os.getenv('DB_PASSWORD', ''), '****')}")
    
    try:
        # Try to execute a simple query to check the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row:
                print("✅ Database connection successful!")
            else:
                print("❌ Database connection failed - query returned no results")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    return True

def check_tables_exist():
    """Check if the expected tables exist in the database."""
    print("\nChecking if tables exist...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"Tables found in the database: {tables}")
    
    expected_tables = ['users', 'rolesTestDine', 'employeesTestDine', 'categoriesTestDine', 
                      'menuTestDine', 'statusTestDine', 'orders', 'order_items', 'bills']
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' doesn't exist")

def check_admin_user():
    """Check if the admin user exists in the database."""
    print("\nChecking for admin user...")
    try:
        with session_scope() as db_session:
            admin = db_session.query(User).filter_by(username='admin').first()
            if admin:
                print(f"✅ Admin user found:")
                print(f"  - Username: {admin.username}")
                print(f"  - Email: {admin.email}")
                print(f"  - Is admin: {admin.is_admin}")
                print(f"  - Password verification test with 'admin123': {admin.check_password('admin123')}")
            else:
                print("❌ No admin user found with username 'admin'")
                
                # Check if there are any users at all
                users_count = db_session.query(User).count()
                print(f"Total users in database: {users_count}")
                
                if users_count > 0:
                    # Show first few users if any exist
                    users = db_session.query(User).limit(5).all()
                    print("Available users:")
                    for user in users:
                        print(f"  - {user.username} (Email: {user.email}, Is admin: {user.is_admin})")
    except Exception as e:
        print(f"❌ Error checking admin user: {str(e)}")

if __name__ == "__main__":
    if check_database_connection():
        check_tables_exist()
        check_admin_user()
    else:
        print("Cannot check tables or users due to database connection failure.")