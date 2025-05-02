from database import session_scope, recreate_database
from models import User
from werkzeug.security import generate_password_hash
import sys

def create_admin_user(recreate=False):
    print("Creating admin user...")
    
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
            
            # Reset password if needed
            if not password_check and '--reset-password' in sys.argv:
                admin_exists.set_password('admin123')
                db_session.add(admin_exists)
                print("Admin password reset to 'admin123'")

if __name__ == "__main__":
    # Pass True to recreate the database if needed
    recreate_arg = '--recreate' in sys.argv
    create_admin_user(recreate=recreate_arg)