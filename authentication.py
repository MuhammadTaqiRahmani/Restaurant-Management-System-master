from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import session_scope
from functools import wraps
import sqlite3
import os
import pyodbc  # Add this import for SQL Server connection

auth = Blueprint("auth", __name__)

# Create a direct SQLite connection for authentication
DB_PATH = "restaurant.db"

# Add SQL Server connection parameters
from dotenv import load_dotenv
load_dotenv(override=True)
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

# Function to get SQL Server connection
def get_sqlserver_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    return pyodbc.connect(conn_str)

# Function to determine if we should use SQL Server instead of SQLite
def use_sql_server():
    # Check if all environment variables are set
    return all([server, database, username, password])

# Updated function to validate employee in either SQLite or SQL Server
def validate_employee(employee_id, username=None):
    if use_sql_server():
        try:
            # Use SQL Server for validation
            conn = get_sqlserver_connection()
            cursor = conn.cursor()
            
            # First try with s_no
            cursor.execute("SELECT * FROM employeesTestDine WHERE s_no = ?", (employee_id,))
            employee = cursor.fetchone()
            
            # If not found and username is provided, try by e_name (SQL Server column name)
            if not employee and username:
                cursor.execute("SELECT * FROM employeesTestDine WHERE e_name = ?", (username,))
                employee = cursor.fetchone()
                
            conn.close()
            return employee
        except Exception as e:
            print(f"SQL Server validation error: {str(e)}")
            # Fall back to SQLite if SQL Server fails
            pass
    
    # Use SQLite as fallback or primary depending on configuration
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # First try with s_no
    cursor.execute("SELECT * FROM employeesTestDine WHERE s_no = ?", (employee_id,))
    employee = cursor.fetchone()
    
    # If not found and username is provided, try by name (SQLite column name)
    if not employee and username:
        cursor.execute("SELECT * FROM employeesTestDine WHERE name = ?", (username,))
        employee = cursor.fetchone()
        
    conn.close()
    return employee

def ensure_users_table():
    """Create users table directly using SQLite if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        print("Creating new SQLite database file")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        employee_id INTEGER NULL
    )
    ''')
    
    # Create employeesTestDine table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employeesTestDine (
        s_no INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        e_role INTEGER,
        salary REAL
    )
    ''')
    
    # Create rolesTestDine table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rolesTestDine (
        s_no INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Check if roles exist in rolesTestDine
    cursor.execute("SELECT COUNT(*) FROM rolesTestDine")
    roles_count = cursor.fetchone()[0]
    
    if roles_count == 0:
        # Insert default roles
        roles = [
            ('Waiter',),
            ('Chef',),
            ('Manager',),
            ('Cashier',),
            ('Kitchen',)
        ]
        cursor.executemany("INSERT INTO rolesTestDine (role) VALUES (?)", roles)
        print("Default roles created in rolesTestDine table")
    
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    admin = cursor.fetchone()
    
    if not admin:
        # Create admin user
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, is_admin, is_active) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@restaurant.com", generate_password_hash("admin123"), True, True)
        )
        print("Admin user created directly in SQLite")
    
    conn.commit()
    conn.close()

# Ensure users table exists and admin user is created
ensure_users_table()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in at all
        if 'user_id' not in session:
            # Clear any potential remaining session data to be safe
            session.clear()
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user exists and is active in the database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (session['user_id'],))
        user = cursor.fetchone()
        
        # If user doesn't exist or was deactivated, clear session and redirect to login
        if not user:
            session.clear()
            flash('Your session has expired. Please login again.', 'error')
            conn.close()
            return redirect(url_for('auth.login'))
        
        # Additional verification for employee roles - verify that the employee's role is still valid
        if not user['is_admin'] and user['employee_id']:
            # Debug - print the employee_id being checked
            print(f"Validating employee with ID: {user['employee_id']}")
            
            # Use our new validation function that works with both SQLite and SQL Server
            employee = validate_employee(user['employee_id'], session.get('username'))
            
            # Handle different return types from SQL Server vs SQLite
            correct_employee_id = None
            if employee:
                # Handle SQL Server pyodbc.Row result
                if use_sql_server() and hasattr(employee, 'cursor_description'):
                    # Get the column index for s_no
                    column_names = [column[0] for column in employee.cursor_description]
                    s_no_index = column_names.index('s_no') if 's_no' in column_names else 0
                    correct_employee_id = employee[s_no_index]
                # Handle SQLite sqlite3.Row result
                elif isinstance(employee, sqlite3.Row):
                    correct_employee_id = employee['s_no']
                # Handle other possibilities for SQL Server return types
                elif hasattr(employee, 's_no'):
                    correct_employee_id = employee.s_no
                # Fallback to indexing if all else fails
                else:
                    try:
                        correct_employee_id = employee[0]  # First column should be s_no
                    except:
                        print(f"Couldn't extract employee_id from result: {type(employee)}")
                
                # If we got a valid employee ID, update the user record if needed
                if correct_employee_id is not None and correct_employee_id != user['employee_id']:
                    cursor.execute("UPDATE users SET employee_id = ? WHERE id = ?", 
                                (correct_employee_id, session['user_id']))
                    conn.commit()
            
            # If employee doesn't exist anymore, invalidate the session
            if not employee or correct_employee_id is None:
                print(f"Employee validation failed: ID {user['employee_id']} not found.")
                
                # Try to get debugging information from both database systems
                if use_sql_server():
                    try:
                        sql_conn = get_sqlserver_connection()
                        sql_cursor = sql_conn.cursor()
                        sql_cursor.execute("SELECT COUNT(*) FROM employeesTestDine")
                        total_employees = sql_cursor.fetchone()[0]
                        print(f"SQL Server: Total employees in DB: {total_employees}")
                        
                        # Show a sample of employee records
                        sql_cursor.execute("SELECT TOP 5 s_no, e_name FROM employeesTestDine")
                        sample_employees = sql_cursor.fetchall()
                        print(f"SQL Server sample employees: {sample_employees}")
                        sql_conn.close()
                    except Exception as e:
                        print(f"Error getting SQL Server debug info: {str(e)}")
                
                # Get SQLite debug info too
                cursor.execute("SELECT COUNT(*) FROM employeesTestDine")
                total_employees = cursor.fetchone()[0]
                print(f"SQLite: Total employees in DB: {total_employees}")
                
                cursor.execute("SELECT s_no, name FROM employeesTestDine LIMIT 5")
                sample_employees = cursor.fetchall()
                print(f"SQLite sample employees: {sample_employees}")
                
                session.clear()
                flash('Your employee account is no longer valid. Please contact an administrator. (Error: Employee ID not found)', 'error')
                conn.close()
                return redirect(url_for('auth.login'))
            else:
                print(f"Employee validation passed: Found employee with ID {correct_employee_id}")
                
        conn.close()
            
        # Check for session timeout (30 minutes)
        if 'last_activity' in session:
            import time
            current_time = time.time()
            if current_time - session['last_activity'] > 1800:  # 30 minutes
                session.clear()
                flash('Your session has timed out due to inactivity. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            session['last_activity'] = current_time
        else:
            # Initialize last_activity if it doesn't exist
            import time
            session['last_activity'] = time.time()
            
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in at all
        if 'user_id' not in session:
            # Clear any potential remaining session data to be safe
            session.clear()
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ? AND is_admin = 1 AND is_active = 1", (session['user_id'],))
        user = cursor.fetchone()
        
        conn.close()
        
        # If user doesn't exist, is not an admin, or was deactivated
        if not user:
            # If user exists but is not admin, redirect to index
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
            if cursor.fetchone():
                flash('You need admin privileges to access this page', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            cursor.close()
            conn.close()
            
            # Otherwise clear session and redirect to login
            session.clear()
            flash('Your session has expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check for session timeout (30 minutes)
        if 'last_activity' in session:
            import time
            current_time = time.time()
            if current_time - session['last_activity'] > 1800:  # 30 minutes
                session.clear()
                flash('Your session has timed out due to inactivity. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            session['last_activity'] = current_time
        else:
            # Initialize last_activity if it doesn't exist
            import time
            session['last_activity'] = time.time()
            
        return f(*args, **kwargs)
    return decorated_function

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Attempting login with username/email: {username}")
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template("login.html")
        
        # Only check SQL Server for users
        user_dict = None
        
        # Check if SQL Server is available
        if use_sql_server():
            try:
                sql_conn = get_sqlserver_connection()
                sql_cursor = sql_conn.cursor()
                
                # Try username match
                sql_cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user_row = sql_cursor.fetchone()
                
                # If not found, try email match
                if not user_row:
                    sql_cursor.execute("SELECT * FROM users WHERE email = ?", (username,))
                    user_row = sql_cursor.fetchone()
                
                if user_row:
                    # Convert row to dictionary
                    user_dict = {
                        'id': user_row.id if hasattr(user_row, 'id') else user_row[0],
                        'username': user_row.username if hasattr(user_row, 'username') else user_row[1],
                        'email': user_row.email if hasattr(user_row, 'email') else user_row[2],
                        'password_hash': user_row.password_hash if hasattr(user_row, 'password_hash') else user_row[3],
                        'is_admin': user_row.is_admin if hasattr(user_row, 'is_admin') else user_row[4],
                        'is_active': user_row.is_active if hasattr(user_row, 'is_active') else user_row[5],
                        'date_joined': user_row.date_joined if hasattr(user_row, 'date_joined') else user_row[6],
                        'employee_id': user_row.employee_id if hasattr(user_row, 'employee_id') else user_row[7]
                    }
                    print(f"Found user in SQL Server: {user_dict['username']}, {user_dict['email']}, admin: {user_dict['is_admin']}")
                
                sql_conn.close()
            except Exception as e:
                print(f"Error checking SQL Server for user: {str(e)}")
                flash(f"Could not connect to the database server. Please try again later or contact an administrator. Error: {str(e)}", "error")
                return render_template("login.html")
        else:
            flash("Database server is not configured. Please contact an administrator.", "error")
            return render_template("login.html")
        
        # If we found a user in the database
        if user_dict:
            # Check password
            if check_password_hash(user_dict['password_hash'], password):
                session['user_id'] = user_dict['id']
                session['username'] = user_dict['username']
                
                # IMPORTANT: Store the admin status in the session
                # Convert is_admin to boolean regardless of source (SQLite or SQL Server might store it differently)
                is_admin_value = bool(user_dict['is_admin'])
                session['is_admin'] = is_admin_value
                
                print(f"Setting is_admin in session to: {is_admin_value}")
                
                # Set session timestamp for inactivity timeout
                import time
                session['last_activity'] = time.time()
                
                # If the user is an admin, redirect to admin dashboard
                if session['is_admin']:
                    flash('Logged in successfully as admin', 'success')
                    return redirect(url_for('index'))
                
                # If the user is linked to an employee, get their role
                employee_id = user_dict['employee_id']
                if employee_id:
                    # Use SQL Server for role lookup
                    try:
                        sql_conn = get_sqlserver_connection()
                        sql_cursor = sql_conn.cursor()
                        
                        # Get the employee's role
                        sql_cursor.execute("""
                            SELECT r.role 
                            FROM employeesTestDine e 
                            JOIN rolesTestDine r ON e.e_role = r.s_no 
                            WHERE e.s_no = ?
                        """, (employee_id,))
                        role_result = sql_cursor.fetchone()
                        
                        sql_conn.close()
                        
                        if role_result:
                            role = role_result[0] if hasattr(role_result, '0') else role_result[0]
                            session['user_role'] = role
                            print(f"User role: {role}")
                            
                            # Redirect based on role
                            if role.lower() == 'waiter':
                                flash(f'Logged in successfully as {role}', 'success')
                                return redirect(url_for('orders'))
                            elif role.lower() == 'chef' or role.lower() == 'kitchen':
                                flash(f'Logged in successfully as {role}', 'success')
                                return redirect(url_for('status'))
                            elif role.lower() == 'manager':
                                flash(f'Logged in successfully as {role}', 'success')
                                return redirect(url_for('management'))
                            elif role.lower() == 'cashier':
                                flash(f'Logged in successfully as {role}', 'success')
                                return redirect(url_for('bill'))
                    except Exception as e:
                        print(f"Error getting employee role: {str(e)}")
                
                # Default redirect if no specific role or role not matched
                flash('Logged in successfully', 'success')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password. Please try again.', 'error')
        else:
            flash(f'No user found with the username or email: {username}', 'error')
    
    return render_template("login.html")

@auth.route("/admin/register", methods=['GET', 'POST'])
@admin_required
def admin_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = 'is_admin' in request.form
        employee_id = request.form.get('employee_id')
        
        # Debugging
        print(f"Admin register form data: username={username}, email={email}, is_admin={is_admin}, employee_id={employee_id}")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.admin_register'))
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
                conn.close()
                return redirect(url_for('auth.admin_register'))
            
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                flash('Email already exists', 'error')
                conn.close()
                return redirect(url_for('auth.admin_register'))
            
            # Create new user
            employee_id_value = int(employee_id) if employee_id and employee_id.isdigit() else None
            
            # Make is_admin a proper boolean for SQLite
            is_admin_value = 1 if is_admin else 0
            
            print(f"Inserting new user: {username}, {email}, is_admin={is_admin_value}, employee_id={employee_id_value}")
            
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, is_admin, employee_id) VALUES (?, ?, ?, ?, ?)",
                (username, email, generate_password_hash(password), is_admin_value, employee_id_value)
            )
            
            conn.commit()
            conn.close()
            
            # Also add the user through SQLAlchemy for better integration
            with session_scope() as session:
                new_user = User(
                    username=username,
                    email=email,
                    is_admin=is_admin,
                    employee_id=employee_id_value
                )
                new_user.set_password(password)
                session.add(new_user)
                # Commit is handled by session_scope context manager
                
            flash('User registered successfully', 'success')
            return redirect(url_for('auth.admin_users'))
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            flash(f'Error registering user: {str(e)}', 'error')
            return redirect(url_for('auth.admin_register'))
    
    return render_template("admin/register_user.html")

@auth.route("/logout")
def logout():
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth.route("/admin/users")
@admin_required
def admin_users():
    try:
        # Use SQL Server connection instead of SQLite
        conn = get_sqlserver_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        users_rows = cursor.fetchall()
        
        users = []
        for row in users_rows:
            # Convert row to dictionary - SQL Server pyodbc doesn't have Row factory
            user_dict = {
                'id': row.id if hasattr(row, 'id') else row[0],
                'username': row.username if hasattr(row, 'username') else row[1],
                'email': row.email if hasattr(row, 'email') else row[2],
                'password_hash': row.password_hash if hasattr(row, 'password_hash') else row[3],
                'is_admin': row.is_admin if hasattr(row, 'is_admin') else row[4],
                'is_active': row.is_active if hasattr(row, 'is_active') else row[5],
                'date_joined': row.date_joined if hasattr(row, 'date_joined') else row[6],
                'employee_id': row.employee_id if hasattr(row, 'employee_id') else row[7]
            }
            users.append(user_dict)
        
        conn.close()
        return render_template("admin/users.html", users=users)
    except Exception as e:
        flash(f"Error retrieving users: {str(e)}", "error")
        return render_template("admin/users.html", users=[])

@auth.route("/admin/users/delete/<int:user_id>", methods=['POST'])
@admin_required
def delete_user(user_id):
    if session.get('user_id') == user_id:
        return jsonify({'status': 'error', 'message': 'You cannot delete your own account'})
    
    # Delete from SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Also delete from SQL Server database
    try:
        sql_conn = get_sqlserver_connection()
        sql_cursor = sql_conn.cursor()
        
        sql_cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        sql_conn.commit()
        sql_conn.close()
    except Exception as e:
        print(f"Error deleting user from SQL Server: {str(e)}")
        # Continue since we at least deleted from SQLite
    
    return jsonify({'status': 'success', 'message': 'User deleted successfully'})

@auth.route("/admin/users/update/<int:user_id>", methods=['POST'])
@admin_required
def update_user(user_id):
    try:
        username = request.form.get('edit_username')
        email = request.form.get('edit_email')
        is_admin = 'edit_is_admin' in request.form
        is_active = 'edit_is_active' in request.form
        employee_id = request.form.get('edit_employee_id')
        password = request.form.get('edit_password')
        confirm_password = request.form.get('edit_confirm_password')
        
        # Debug info
        print(f"Updating user ID {user_id}: username={username}, email={email}, is_admin={is_admin}, is_active={is_active}, employee_id={employee_id}")
        print(f"Form data: {dict(request.form)}")
        
        if not username or not email:
            return jsonify({'status': 'error', 'message': 'Username and email are required'}), 400
        
        # Check passwords match if provided
        if password and password != confirm_password:
            return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
        
        # Track if admin status is being changed for the current logged-in user
        requires_relogin = False
        current_admin_status = None
        
        # Use SQL Server as the primary database
        user_exists = False
        update_successful = False
        
        # First update in SQL Server database (primary)
        if use_sql_server():
            try:
                sql_conn = get_sqlserver_connection()
                sql_cursor = sql_conn.cursor()
                
                # Check if user exists in SQL Server
                sql_cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_sql = sql_cursor.fetchone()
                
                if user_sql:
                    user_exists = True
                    # Save current admin status to check if it's being changed
                    current_admin_status = bool(user_sql.is_admin if hasattr(user_sql, 'is_admin') else user_sql[4])
                    
                    # Check if another user already has this username (excluding the current user)
                    sql_cursor.execute("SELECT * FROM users WHERE username = ? AND id != ?", (username, user_id))
                    if sql_cursor.fetchone():
                        sql_conn.close()
                        return jsonify({'status': 'error', 'message': 'Username already taken by another user in SQL Server'}), 400
                    
                    # Check if another user already has this email (excluding the current user)
                    sql_cursor.execute("SELECT * FROM users WHERE email = ? AND id != ?", (email, user_id))
                    if sql_cursor.fetchone():
                        sql_conn.close()
                        return jsonify({'status': 'error', 'message': 'Email already in use by another user in SQL Server'}), 400
                    
                    # Convert form values to appropriate types
                    employee_id_value = None
                    if employee_id and employee_id.strip():
                        try:
                            employee_id_value = int(employee_id)
                        except ValueError:
                            employee_id_value = None
                    
                    # Handle checkbox values properly
                    is_admin_value = 1 if is_admin else 0
                    is_active_value = 1 if is_active else 0
                    
                    print(f"Updating SQL Server with values: admin={is_admin_value}, active={is_active_value}")
                    
                    # Check if we need to update the password
                    if password:
                        # Update SQL Server record with new password
                        sql_cursor.execute("""
                            UPDATE users 
                            SET username = ?, email = ?, password_hash = ?, is_admin = ?, is_active = ?, employee_id = ? 
                            WHERE id = ?
                        """, (username, email, generate_password_hash(password), is_admin_value, is_active_value, employee_id_value, user_id))
                    else:
                        # Update without changing password
                        sql_cursor.execute("""
                            UPDATE users 
                            SET username = ?, email = ?, is_admin = ?, is_active = ?, employee_id = ? 
                            WHERE id = ?
                        """, (username, email, is_admin_value, is_active_value, employee_id_value, user_id))
                    
                    sql_conn.commit()
                    update_successful = True
                    print(f"Updated user {user_id} in SQL Server database")
                
                sql_conn.close()
            except Exception as sql_e:
                print(f"Error updating user in SQL Server: {str(sql_e)}")
                return jsonify({'status': 'error', 'message': f'Database error: {str(sql_e)}'}), 500
        
        # Try to also update in SQLite for backup purposes, but don't fail if it has issues
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if the user exists in SQLite
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_sqlite = cursor.fetchone()
            
            if user_sqlite:
                user_exists = True
                # If current_admin_status isn't set yet, get it from SQLite
                if current_admin_status is None and user_sqlite:
                    current_admin_status = bool(user_sqlite[4])  # SQLite is_admin column
                
                # Convert form values to appropriate types
                employee_id_value = None
                if employee_id and employee_id.strip():
                    try:
                        employee_id_value = int(employee_id)
                    except ValueError:
                        employee_id_value = None
                
                # Handle checkbox values properly
                is_admin_value = 1 if is_admin else 0
                is_active_value = 1 if is_active else 0
                
                # Check if we need to update the password
                if password:
                    # Update SQLite record with new password
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, email = ?, password_hash = ?, is_admin = ?, is_active = ?, employee_id = ? 
                        WHERE id = ?
                    """, (username, email, generate_password_hash(password), is_admin_value, is_active_value, employee_id_value, user_id))
                else:
                    # Update without changing password
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, email = ?, is_admin = ?, is_active = ?, employee_id = ? 
                        WHERE id = ?
                    """, (username, email, is_admin_value, is_active_value, employee_id_value, user_id))
                
                conn.commit()
                print(f"Updated user {user_id} in SQLite database")
            
            conn.close()
        except Exception as sqlite_e:
            # Don't fail if SQLite update fails, just log the error
            print(f"Warning: Error updating user in SQLite (not critical): {str(sqlite_e)}")
            # Continue since the SQL Server update is what matters most
        
        if not user_exists and not update_successful:
            return jsonify({'status': 'error', 'message': 'User not found in any database'}), 404
        
        # Check if admin status is being changed for the current logged-in user
        if 'user_id' in session and int(session['user_id']) == user_id:
            old_is_admin = current_admin_status if current_admin_status is not None else session.get('is_admin', False)
            if bool(old_is_admin) != bool(is_admin):
                requires_relogin = True
                print(f"Admin status changed for current user from {old_is_admin} to {is_admin}")
            
            # IMPORTANT: Update the session immediately so permissions take effect right away
            print(f"Updating session for user {user_id} with new admin status: {is_admin}")
            session['is_admin'] = bool(is_admin)
            session['username'] = username
            
            # Flash messages for the user if their account was changed
            if bool(old_is_admin) != bool(is_admin):
                if is_admin:
                    flash('Your account has been granted admin privileges. You now have access to the Admin Panel.', 'success')
                else:
                    flash('Your admin privileges have been revoked. You will be redirected to the appropriate portal on your next login.', 'info')
        
        # Create a user dict for JSON response
        user_dict = {
            'id': user_id,
            'username': username,
            'email': email,
            'is_admin': bool(is_admin),
            'is_active': bool(is_active),
            'employee_id': employee_id_value if 'employee_id_value' in locals() else employee_id,
            'requires_relogin': requires_relogin
        }
        
        # Flash a success message
        flash('User updated successfully', 'success')
        
        # For AJAX requests, return success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success', 
                'message': 'User updated successfully',
                'user': user_dict,
                'requiresRelogin': requires_relogin
            })
        
        return redirect(url_for('auth.admin_users'))
            
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': f'Error updating user: {str(e)}'}), 500
        flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('auth.admin_users'))

