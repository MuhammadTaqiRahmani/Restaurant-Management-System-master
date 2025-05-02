from database_sqlite import session_scope, recreate_database, Base
from models import User
from werkzeug.security import generate_password_hash
import sys

# Import all models to ensure they're registered with Base
from models import User, Roles, Employees, Category, Menu, Status, Order, OrderItem, Bill

def create_admin_user(recreate=False):
    print("Creating admin user in SQLite database...")
    
    if recreate:
        print("Recreating database tables...")
        recreate_database()
        print("Database tables recreated.")
    
    with session_scope() as db_session:
        # Check if admin user already exists
        admin_exists = db_session.query(User).filter_by(username='admin').first()
        
        if not admin_exists:
            # Create admin user with proper password hashing
            admin_user = User(
                username='admin',
                email='admin@restaurant.com',
                is_admin=True,
                is_active=True
            )
            
            # Set password - this will use the proper hashing method
            admin_user.set_password('admin123')
            
            try:
                db_session.add(admin_user)
                db_session.commit()
                print("Admin user created successfully!")
                print("Username: admin")
                print("Email: admin@restaurant.com")
                print("Password: admin123")
                
                # Verify user was created
                user = db_session.query(User).filter_by(username='admin').first()
                if user:
                    print(f"Verified user exists with id: {user.id}")
                    password_check = user.check_password('admin123')
                    print(f"Password check result: {password_check}")
            except Exception as e:
                db_session.rollback()
                print(f"Error creating admin user: {str(e)}")
        else:
            print("Admin user already exists in the database.")
            print(f"User ID: {admin_exists.id}")
            print(f"Username: {admin_exists.username}")
            print(f"Email: {admin_exists.email}")
            
            # Test password verification
            password_check = admin_exists.check_password('admin123')
            print(f"Password check result: {password_check}")

if __name__ == "__main__":
    # Pass True to recreate the database if needed
    recreate_arg = '--recreate' in sys.argv
    create_admin_user(recreate=recreate_arg)