import base64
from collections import defaultdict
import io
import os
import csv
from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for, Response
from sqlalchemy.orm import sessionmaker, joinedload
from models import OrderItem, Roles, Employees, Category, Menu, Status, Order, User, MonthlySales, YearlySales
from database import engine, session_scope, recreate_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from models import Bill
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import extract
from authentication import auth, login_required, admin_required
from sales_helpers import update_monthly_sales, update_yearly_sales, get_monthly_sales_data, get_yearly_sales_data, process_historical_sales_data
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import os, json, csv, io
from functools import wraps

app = Flask(__name__)
app.config['STATIC_BASE_URL'] = os.getenv('STATIC_BASE_URL', '/static')
app.secret_key = 'Anti_Minsh'
# Register the authentication blueprint
app.register_blueprint(auth, url_prefix='/')

# IMPORTANT: Comment out this line after first run - it will DELETE ALL DATA each time the app starts
# recreate_database()  # Commented out to prevent database recreation on server restart

# Initialize sales data tables
def initialize_sales_data():
    with session_scope() as db_session:
        # Check if monthly_sales table has data
        monthly_data_exists = db_session.query(MonthlySales).first() is not None
        if not monthly_data_exists:
            print("Initializing sales data...")
            # Create dummy sales data for current year
            current_year = datetime.now().year
            for month in range(1, 13):
                monthly_sales = MonthlySales(
                    year=current_year,
                    month=month,
                    total_sales=0.0,
                    order_count=0
                )
                db_session.add(monthly_sales)
            
            # Create a yearly sales record for current year
            yearly_sales = YearlySales(
                year=current_year,
                total_sales=0.0,
                order_count=0
            )
            db_session.add(yearly_sales)
            db_session.commit()
            print("Sales data initialized successfully")
        else:
            print("Sales data already exists, skipping initialization")

# Create initial admin user function
def create_initial_admin():
    print("Attempting to create admin user...")
    with session_scope() as db_session:
        admin_exists = db_session.query(User).filter_by(username='admin').first()
        if not admin_exists:
            try:
                admin_user = User(
                    username='admin',
                    email='admin@restaurant.com',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db_session.add(admin_user)
                db_session.commit()
                print("Admin user created successfully with username 'admin' and password 'admin123'")
            except Exception as e:
                print(f"Error creating admin user: {str(e)}")
                db_session.rollback()
        else:
            print("Admin user already exists in the database")

# Initialize admin user with a proper setup event
@app.before_request
def before_first_request():
    # Use a session flag to ensure this runs only once
    if not session.get('_initial_setup_done'):
        create_initial_admin()
        initialize_sales_data()  # Initialize sales data tables
        session['_initial_setup_done'] = True

# Inject user data into all templates
@app.context_processor
def inject_user():
    user_data = None
    if 'user_id' in session:
        with session_scope() as db_session:
            user = db_session.query(User).filter_by(id=session['user_id']).first()
            if user:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': bool(user.is_admin),  # Ensure is_admin is properly cast to boolean
                    'is_active': user.is_active,
                    'employee_id': user.employee_id
                }
                
                # Add user_role to the object if it exists in session
                if 'user_role' in session:
                    user_data['user_role'] = session['user_role']
    
    # If we couldn't get user data from the database but have session data, use that as fallback
    if user_data is None and 'user_id' in session:
        user_data = {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'is_admin': bool(session.get('is_admin', False)),  # Ensure is_admin is properly cast to boolean
            'user_role': session.get('user_role', 'Employee')
        }
    
    print(f"Context user data: {user_data}")  # Debug print to see what's being provided to templates
    return dict(current_user=user_data)

@app.route("/")
@login_required
def index():
    with session_scope() as db_session:
        order_items = db_session.query(OrderItem).options(joinedload(OrderItem.menu_item)).all()
        bills = db_session.query(Bill).all()

        # Process data to get sales frequency of each item
        sales_frequency = {}
        for item in order_items:
            menu_item_name = item.menu_item.item
            sales_frequency[menu_item_name] = sales_frequency.get(menu_item_name, 0) + item.quantity

        labels = list(sales_frequency.keys())
        data = list(sales_frequency.values())

        # Process data for the area chart
        minute_profit = defaultdict(int)
        for bill in bills:
            minute = bill.time.strftime('%Y-%m-%d %H:%M')  # Aggregate by minute
            minute_profit[minute] += bill.calculate_total()

        # Sort the data by time
        sorted_minutes = sorted(minute_profit.keys())
        area_chart_labels = sorted_minutes
        area_chart_data = [minute_profit[minute] for minute in sorted_minutes]
        
        total_orders = db_session.query(Order).count()
        total_customers = db_session.query(Status).count()
        total_employees = db_session.query(Employees).count()

    return render_template("index.html", 
                           labels=labels, 
                           data=data,
                           area_chart_labels=area_chart_labels, 
                           area_chart_data=area_chart_data,
                           total_orders=total_orders,
                           total_customers=total_customers,
                           total_employees=total_employees)


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/table")
@login_required
def table():
    return render_template("basic-table.html")


@app.route("/management")
@login_required
@admin_required
def management():
    return render_template("Managementib.html")

@app.route("/months")
@login_required
def months():
    year = request.args.get('year', type=int)
    if year is None:
        year = datetime.now().year
    
    monthly_data = get_monthly_sales_data(year)
    
    # Get list of available years for the dropdown
    with session_scope() as db_session:
        available_years = db_session.query(extract('year', Bill.time).distinct()).order_by(extract('year', Bill.time)).all()
        available_years = [int(year[0]) for year in available_years]
        if not available_years:  # Fallback if no data exists
            available_years = [datetime.now().year]
            
    return render_template("months.html", monthly_sales=monthly_data, 
                          current_year=year, available_years=available_years)

@app.route("/years")
@login_required
def years():
    # Get yearly sales data for the past 5 years by default
    yearly_data = get_yearly_sales_data()
    
    return render_template("years.html", yearly_sales=yearly_data)

# Add this new route to process historical sales data (admin only)
@app.route("/process_historical_sales", methods=['POST'])
@login_required
@admin_required
def process_sales_history():
    try:
        process_historical_sales_data()
        return jsonify({'status': 'success', 'message': 'Historical sales data processed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing historical data: {str(e)}'}), 500

# Add a new route for sales dashboard
@app.route("/sales_dashboard")
@login_required
def sales_dashboard():
    # Get monthly data for current year
    monthly_data = get_monthly_sales_data()
    
    # Get yearly data for the past 5 years
    yearly_data = get_yearly_sales_data()
    
    # Calculate some aggregate statistics
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    current_month_sales = next((item['total_sales'] for item in monthly_data if item['month_num'] == current_month), 0)
    
    # Find previous month's sales
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_month_year = current_year if current_month > 1 else current_year - 1
    prev_month_sales = next(
        (item['total_sales'] for item in monthly_data if item['month_num'] == prev_month), 
        0
    )
    
    # Calculate month-over-month growth
    if prev_month_sales > 0:
        mom_growth = ((current_month_sales - prev_month_sales) / prev_month_sales) * 100
    else:
        mom_growth = 100  # If no previous sales, growth is 100%
    
    # Find current year sales
    current_year_sales = next((item['total_sales'] for item in yearly_data if item['year'] == current_year), 0)
    
    # Find previous year's sales
    prev_year = current_year - 1
    prev_year_sales = next(
        (item['total_sales'] for item in yearly_data if item['year'] == prev_year), 
        0
    )
    
    # Calculate year-over-year growth
    if prev_year_sales > 0:
        yoy_growth = ((current_year_sales - prev_year_sales) / prev_year_sales) * 100
    else:
        yoy_growth = 100  # If no previous sales, growth is 100%
        
    return render_template("sales_dashboard.html", 
                          monthly_data=monthly_data,
                          yearly_data=yearly_data,
                          current_month_sales=current_month_sales,
                          current_year_sales=current_year_sales,
                          mom_growth=mom_growth,
                          yoy_growth=yoy_growth)

@app.route("/bill")
@login_required
def bill():
    with session_scope() as db_session:
        # Query to get unique customer_status_id
        customer_status_ids = db_session.query(Order.customer_status_id).distinct().all()
        
        # Compute total bill for each customer_status_id
        customer_bills = db_session.query(
            Order.customer_status_id,
            func.sum(OrderItem.quantity * Menu.price).label('total_bill')
        ).join(OrderItem, Order.id == OrderItem.order_id)\
         .join(Menu, Menu.s_no == OrderItem.menu_item_id)\
         .group_by(Order.customer_status_id).all()

    # Convert the results to dictionaries for easier template rendering
    customer_status_ids_dict = {cid[0]: 0 for cid in customer_status_ids}
    customer_bills_dict = {cb[0]: cb[1] for cb in customer_bills}

    # Merge the two dictionaries, ensuring every customer_status_id is included
    for cid in customer_status_ids_dict:
        if cid in customer_bills_dict:
            customer_status_ids_dict[cid] = customer_bills_dict[cid]

    return render_template("bill.html", customer_status_ids_dict=customer_status_ids_dict)

@app.route("/generate_bill/<int:order_id>", methods=['POST'])
@login_required
def generate_bill(order_id):
    with session_scope() as db_session:
        # Check if bill already exists for this order
        existing_bill = db_session.query(Bill).filter(Bill.order_id == order_id).first()
        if existing_bill:
            return jsonify({'status': 'error', 'message': 'Bill already generated for this order'}), 400
            
        order = db_session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
            
        # Calculate bill total
        order_items = db_session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        total_bill = sum(
            item.menu_item.price * item.quantity 
            for item in order_items
        )
        
        # Create new bill
        bill = Bill(order_id=order.id, total=total_bill)
        db_session.add(bill)
        db_session.flush()  # Flush to get the bill ID
        
        # Update monthly and yearly sales data
        update_monthly_sales(total_bill, bill.time)
        update_yearly_sales(total_bill, bill.time)
        
        db_session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Bill generated successfully',
            'bill_id': bill.id,
            'total': bill.total
        })

@app.route("/roles", methods=['GET', 'POST'])
@login_required
@admin_required
def roles():
    if request.method == 'POST':
        role = request.form.get('role')

        with session_scope() as db_session:
            existing_role = db_session.query(Roles).filter(Roles.role == role).first()
            if existing_role is None:
                entry = Roles(role=role)
                db_session.add(entry)

    with session_scope() as db_session:
        roles = db_session.query(Roles).options(joinedload('*')).order_by(Roles.s_no).all()
        roles = [role.to_dict() for role in roles]
    return render_template("roles.html", roles=roles)

@app.route("/roles/delete/<int:role_id>", methods=['POST'])
@login_required
@admin_required
def delete_role(role_id):
    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
        if role:
            db_session.delete(role)
    return jsonify({'status': 'success', 'message': 'Role deleted successfully'})

@app.route("/roles/update/<int:role_id>", methods=['POST'])
@login_required
@admin_required
def update_role(role_id):
    role_name = request.form.get('edit_role')
    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
        if role:
            role.role = role_name
            db_session.add(role)
    return jsonify({'status': 'success', 'message': 'Role updated successfully'})

@app.route("/employees", methods=['GET', 'POST'])
@login_required
@admin_required
def employee():
    if request.method == 'POST':
        e_name = request.form.get('e_name')
        role_name = request.form.get('role_id')

        with session_scope() as db_session:
            role = db_session.query(Roles).filter(Roles.role == role_name).first()
            if role:
                entry = Employees(e_name=e_name, e_role=role.s_no)
                db_session.add(entry)
            else:
                return jsonify({'status': 'error', 'message': 'Role not found'}), 400

    with session_scope() as db_session:
        employees = db_session.query(Employees.s_no, Employees.e_name, Roles.role).join(Roles, Employees.e_role == Roles.s_no).order_by(Employees.s_no.asc()).all()
        roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
        roles = [role.to_dict() for role in roles]

    return render_template("Employees.html", employees=employees, roles=roles)


@app.route("/employees/delete/<int:employee_id>", methods=['POST'])
@login_required
@admin_required
def delete_employee(employee_id):
    try:
        with session_scope() as db_session:
            # First check if there are any users associated with this employee
            user = db_session.query(User).filter(User.employee_id == employee_id).first()
            if user:
                # Option 1: Set the employee_id to NULL for the associated user
                user.employee_id = None
                # Option 2 (alternative): Delete the associated user
                # db_session.delete(user)
                
            # Now delete the employee
            employee = db_session.query(Employees).filter(Employees.s_no == employee_id).first()
            if employee:
                db_session.delete(employee)
                
        return jsonify({'status': 'success', 'message': 'Employee deleted successfully'})
    except Exception as e:
        # Log the error for debugging
        print(f"Error deleting employee: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to delete employee. Error: ' + str(e)}), 500


@app.route("/employees/update/<int:employee_id>", methods=['POST'])
@login_required
@admin_required
def update_employee(employee_id):
    emp_name = request.form.get('edit_name')
    emp_role_name = request.form.get('edit_role')

    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.role == emp_role_name).first()
        if role:
            employee = db_session.query(Employees).filter(Employees.s_no == employee_id).first()
            if employee:
                employee.e_name = emp_name
                employee.e_role = role.s_no
                db_session.add(employee)
    return jsonify({'status': 'success', 'message': 'Employee updated successfully'})


@app.route("/categories", methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        cat = request.form.get('cat')
        entry = Category(cat=cat)

        try:
            with session_scope() as db_session:
                db_session.add(entry)
                db_session.commit()
        except IntegrityError:
            flash('Category should be unique', 'error')

    with session_scope() as db_session:
        cats = db_session.query(Category).order_by(Category.s_no.asc()).all()
        cats = [cat.to_dict() for cat in cats]

    return render_template("foodCategories.html", cats=cats)

@app.route("/categories/delete/<int:cat_id>", methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.s_no == cat_id).first()
        if category:
            db_session.delete(category)
    return jsonify({'status': 'success', 'message': 'Category deleted successfully'})


@app.route("/categories/update/<int:cat_id>", methods=['POST'])
@login_required
@admin_required
def update_category(cat_id):
    cat_name = request.form.get('edit_cat')
    with session_scope() as db_session:
        # Check if the category name already exists
        existing_category = db_session.query(Category).filter(Category.cat == cat_name).first()
        if existing_category:
            return jsonify({'status': 'error', 'message': 'Category has been already saved'})

        # Update the category if no duplicate is found
        category = db_session.query(Category).filter(Category.s_no == cat_id).first()
        if category:
            category.cat = cat_name
            db_session.add(category)
            db_session.commit()
            return jsonify({'status': 'success', 'message': 'Category updated successfully'})
        return jsonify({'status': 'error', 'message': 'Category not found'})

@app.route("/menu", methods=['GET', 'POST'])
@login_required
def menu():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        if request.method == 'POST':
            item = request.form.get('item')
            price = int(request.form.get('price'))  
            cat_id = int(request.form.get('cat_id'))
            status = request.form.get('status')
            
            print(f"Category ID: {cat_id}")
            entry = Menu(item=item, price=price, category=cat_id, status=status)
            session.add(entry) 
            session.commit()

        items = session.query(Menu).options(joinedload(Menu.category_rel)).order_by(Menu.s_no.asc()).all()


        items = [item.to_list() for item in items]
        categories = session.query(Category).order_by(Category.s_no.asc()).all()
        categories = [category.to_dict() for category in categories]

        print(f"Items: {items}")
        print(f"Categories: {categories}")

        session.close()

        return render_template("menu.html", items=items, categories=categories)
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500



@app.route("/menu/delete/<int:item_id>", methods=['POST'])
@login_required
@admin_required
def delete_menu_item(item_id):
    with session_scope() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.s_no == item_id).first()
        if menu_item:
            db_session.delete(menu_item)
    return jsonify({'status': 'success', 'message': 'Menu item deleted successfully'})


@app.route("/menu/update/<int:item_id>", methods=['POST'])
@login_required
@admin_required
def update_menu_item(item_id):
    item_name = request.form.get('edit_item_name')
    price = request.form.get('edit_price')
    cat_id = request.form.get('edit_cat_id')
    status = request.form.get('edit_status')

    with session_scope() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.s_no == item_id).first()
        if menu_item:
            menu_item.item = item_name
            menu_item.price = price
            
            category_obj = db_session.query(Category).filter(Category.s_no == cat_id).first()
            if category_obj:
                menu_item.category = cat_id
            
            menu_item.status = status
            db_session.add(menu_item)

            updated_item = {
                "s_no": menu_item.s_no,
                "item": menu_item.item,
                "price": menu_item.price,
                "category": category_obj.cat if category_obj else '',
                "status": menu_item.status
            }
    
    return jsonify({'status': 'success', 'message': 'Menu item updated successfully', 'item': updated_item})

# validation of item wheather it is available or not
@app.route("/menu/check_availability/<int:item_id>", methods=['GET'])
@login_required
def check_availability(item_id):
    with session_scope() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.s_no == item_id).first()
        if menu_item and menu_item.status == 'Available':
            return jsonify({'status': 'available'})
        else:
            return jsonify({'status': 'unavailable'})
        
# --------------------------


@app.route("/status", methods=['GET', 'POST'])
@login_required
def status():
    if request.method == 'POST':
        floor = request.form.get('floor')
        category = request.form.get('category')
        customer = int(request.form.get('customer'))
        table_no = request.form.get('table_no')

        with session_scope() as db_session:
            # Calculate current occupied tables on the selected floor
            occupied_tables = db_session.query(Status).filter(Status.floor == floor).count()
            
            # Check if adding another table exceeds the capacity (15 tables per floor)
            if occupied_tables >= 15:
                flash('Floor has no capacity', 'error')
            else:
                entry = Status(floor=floor, category=category, customer=customer, table_no=table_no)
                db_session.add(entry)

        # Redirect to the status page after processing the form
        return redirect('/status')

    # If it's a GET request, render the status template with current data
    with session_scope() as db_session:
        statuses = db_session.query(Status).order_by(Status.s_no.asc()).all()
        statuses = [status.to_list() for status in statuses]
    
    floor_status = {
        'Ground Floor': sum(1 for status in statuses if status[1] == 'Ground Floor'),
        '1st Floor': sum(1 for status in statuses if status[1] == '1st Floor'),
        '2nd Floor': sum(1 for status in statuses if status[1] == '2nd Floor')
    }

    return render_template("status.html", statuses=statuses, floor_status=floor_status)


@app.route("/status/delete/<int:id>", methods=['POST'])
@login_required
@admin_required
def delete_status(id):
    with session_scope() as db_session:
        status = db_session.query(Status).filter_by(s_no=id).first()
        if status:
            db_session.delete(status)
            db_session.commit()
            return jsonify({'status': 'success', 'message': 'Status deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Status not found'}), 404

        
        
@app.route("/status/update/<int:id>", methods=['POST'])
@login_required
@admin_required
def update_status(id):
    floor = request.form.get('edit_floor')
    category = request.form.get('edit_category')
    customer = request.form.get('edit_customer')
    table_no = request.form.get('edit_table_no')

    with session_scope() as db_session:
        status = db_session.query(Status).filter(Status.s_no == id).first()
        if status:
            current_floor = status.floor
            
            # Calculate current occupied tables on the selected floor
            occupied_tables = db_session.query(Status).filter(Status.floor == floor).count()
            
            # Check if updating to another floor exceeds the capacity (15 tables per floor)
            if floor != current_floor and occupied_tables >= 15:
                return jsonify({'status': 'error', 'message': 'Floor has no capacity'}), 400
            
            # Update the status if capacity allows
            status.floor = floor
            status.category = category
            status.customer = customer
            status.table_no = table_no
            db_session.add(status)
            updated_status = {
                "s_no": status.s_no,
                "floor": status.floor,
                "category": status.category,
                "customer": status.customer,
                "table_no": status.table_no
            }
            return jsonify({'status': 'success', 'message': 'Status updated successfully', 'item': updated_status})
        else:
            return jsonify({'status': 'error', 'message': 'Status not found'}), 404


@app.route("/orders", methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        customer_status_id = request.form.get('customer_status_id')

        with session_scope() as db_session:
            status = db_session.query(Status).filter(Status.s_no == customer_status_id).first()
            if status:
                new_order = Order(customer_status_id=customer_status_id)
                db_session.add(new_order)
                db_session.commit()

    with session_scope() as db_session:
        orders = db_session.query(Order).all()
        orders_list = []

        for order in orders:
            order_data = get_orders_data(order.id)
            if order_data:
                orders_list.append({
                    'id': order.id,
                    'customer_status_id': order.customer_status_id,
                    'total_bill': order_data['total_bill']
                })

    return render_template("orders.html", orders=orders_list)


@app.route("/orders/delete/<int:order_id>", methods=['POST'])
@login_required
@admin_required
def delete_order(order_id):
    with session_scope() as db_session:
        order = db_session.query(Order).filter(Order.id == order_id).first()
        if order:
            # Delete associated order items first
            db_session.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
            # Then delete the order
            db_session.delete(order)
    return jsonify({'status': 'success', 'message': 'Order deleted successfully'})


def get_orders_data(order_id):
    with session_scope() as db_session:
        order = db_session.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None 
        
        order_items = db_session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        order_data = {
            'order_id': order.id,
            'customer_status_id': order.customer_status_id,
            'items': [],
            'total_bill': 0  # Initialize total bill
        }
        
        total_bill = 0  # Initialize total bill calculation
        
        for item in order_items:
            menu_item = db_session.query(Menu).filter(Menu.s_no == item.menu_item_id).first()
            item_price = menu_item.price if menu_item else 0
            aggregate_price = item.quantity * item_price
            total_bill += aggregate_price
            
            order_data['items'].append({
                'menu_item_id': item.menu_item_id,
                'menu_item_name': menu_item.item if menu_item else 'Unknown',
                'quantity': item.quantity,
                'price': item_price,
                'aggregate_price': aggregate_price
            })
        
        order_data['total_bill'] = total_bill  # Set the total bill
        
        return order_data


@app.route("/orderinfo/<int:order_id>", methods=['GET', 'POST'])
@login_required
def order_info(order_id):
    if request.method == 'POST':
        try:
            menu_item_id = int(request.form.get('menu_item_id', 0))
            quantity = int(request.form.get('quantity', 0))

            if menu_item_id <= 0 or quantity <= 0:
                flash("Invalid menu item ID or quantity.", "error")
                return redirect(url_for('order_info', order_id=order_id))

            with session_scope() as db_session:
                order_item = OrderItem(order_id=order_id, menu_item_id=menu_item_id, quantity=quantity)
                db_session.add(order_item)
                db_session.commit()
                flash("Item added successfully.", "success")

        except ValueError:
            flash("Invalid input. Please enter valid numbers.", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('order_info', order_id=order_id))
    

    orders_data = get_orders_data(order_id)
    print(f"Orders Data: {orders_data}")
    return render_template("orderinfo.html", order_id=order_id, orders_data=orders_data)

@app.route("/orderinfo/delete/<int:menu_item_id>", methods=['POST'])
@login_required
def delete_order_item(menu_item_id):
    try:
        with session_scope() as db_session:
            order_item = db_session.query(OrderItem).filter(OrderItem.menu_item_id == menu_item_id).first()
            if order_item:
                db_session.delete(order_item)
                db_session.commit()
                return jsonify({'status': 'success', 'message': 'Order item deleted successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Order item not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route("/orderinfo/update/<int:menu_item_id>", methods=['POST'])
@login_required
def update_order_item(menu_item_id):
    try:
        quantity = int(request.form.get('edit_quantity'))

        with session_scope() as db_session:
            order_item = db_session.query(OrderItem).filter(OrderItem.menu_item_id == menu_item_id).first()
            if order_item:
                order_item.quantity = quantity
                db_session.add(order_item)
                db_session.commit()
                return jsonify({'status': 'success', 'message': 'Order item quantity updated successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Order item not found'}), 404
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid quantity format'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/export_monthly_sales/<int:year>", methods=['GET'])
@login_required
@admin_required
def export_monthly_sales(year):
    """Export monthly sales data for a specific year as CSV"""
    monthly_data = get_monthly_sales_data(year)
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Month', 'Year', 'Total Sales', 'Order Count', 'Average Order Value'])
    
    # Write data rows
    for month in monthly_data:
        writer.writerow([
            month['month'], 
            month['year'], 
            month['total_sales'], 
            month['order_count'],
            month['average_order'] if month['order_count'] > 0 else 0
        ])
    
    # Prepare the response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=monthly_sales_{year}.csv"}
    )

@app.route("/export_yearly_sales", methods=['GET'])
@login_required
@admin_required
def export_yearly_sales():
    """Export yearly sales data as CSV"""
    # Get the date range parameters
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    
    yearly_data = get_yearly_sales_data(start_year, end_year)
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Year', 'Total Sales', 'Order Count', 'Average Order Value'])
    
    # Write data rows
    for year in yearly_data:
        writer.writerow([
            year['year'], 
            year['total_sales'], 
            year['order_count'],
            year['average_order'] if year['order_count'] > 0 else 0
        ])
    
    # Prepare the response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=yearly_sales_data.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")