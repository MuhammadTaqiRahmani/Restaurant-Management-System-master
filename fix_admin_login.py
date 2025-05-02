from database import session_scope, engine, Base
from models import User
from sqlalchemy import inspect, text
import sys

def fix_admin_login():
    """
    This script ensures the admin user exists in the database and is properly configured.
    It will:
    1. Check if the users table exists
    2. Create the users table if needed
    3. Check if admin user exists
    4. Create or update admin user with correct password
    """
    print("Starting admin login fix...")
    
    # Check if the users table exists
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Existing tables: {tables}")
    
    # Create the users table if it doesn't exist
    if 'users' not in tables:
        print("Creating users table...")
        # Only create the User table, not all tables
        User.__table__.create(engine, checkfirst=True)
        print("Users table created.")
    
    # Now check if admin user exists or create it
    with session_scope() as db_session:
        admin = db_session.query(User).filter_by(username='admin').first()
        
        if admin:
            print(f"Admin user found (ID: {admin.id})")
            # Reset admin password just in case
            admin.set_password('admin123')
            admin.is_admin = True
            admin.is_active = True
            admin.email = 'admin@restaurant.com'
            print("Admin user credentials reset.")
        else:
            print("Admin user not found. Creating new admin user...")
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@restaurant.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db_session.add(admin)
        
        try:
            db_session.commit()
            print("Admin user saved successfully!")
            print("Admin login details:")
            print("Username: admin")
            print("Password: admin123")
            print("Email: admin@restaurant.com")
            
            # Verify the user can be found and password works
            admin = db_session.query(User).filter_by(username='admin').first()
            if admin:
                print(f"Verification: Admin user exists with ID: {admin.id}")
                password_check = admin.check_password('admin123')
                print(f"Password check result: {password_check}")
                print(f"Admin status: {admin.is_admin}")
            else:
                print("WARNING: Admin user couldn't be verified after save!")
                
        except Exception as e:
            print(f"Error saving admin user: {str(e)}")

if __name__ == "__main__":
    fix_admin_login()