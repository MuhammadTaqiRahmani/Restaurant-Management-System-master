import os
from flask import Flask, flash, redirect,render_template,request, jsonify, session, url_for
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from models import OrderItem, Roles, Employees, Category, Menu, Status, Order
from database import engine, session_scope, recreate_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
from models import Bill
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['STATIC_BASE_URL'] = os.getenv('STATIC_BASE_URL', '/static')
app.secret_key = 'Anti_Minsh'
# recreate_database()

# creating routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/chart")
def chartjs():
    return render_template("chartjs.html")

@app.route("/table")
def table():
    return render_template("basic-table.html")


@app.route("/management")
def management():
    return render_template("Managementib.html")

@app.route("/months")
def months():
    return render_template("days.html")

@app.route("/years")
def years():
    return render_template("months.html")


@app.route("/bill")
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



@app.route("/roles", methods=['GET', 'POST'])
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
def delete_role(role_id):
    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
        if role:
            db_session.delete(role)
    return jsonify({'status': 'success', 'message': 'Role deleted successfully'})

@app.route("/roles/update/<int:role_id>", methods=['POST'])
def update_role(role_id):
    role_name = request.form.get('edit_role')
    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
        if role:
            role.role = role_name
            db_session.add(role)
    return jsonify({'status': 'success', 'message': 'Role updated successfully'})

@app.route("/employees", methods=['GET', 'POST'])
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
def delete_employee(employee_id):
    with session_scope() as db_session:
        employee = db_session.query(Employees).filter(Employees.s_no == employee_id).first()
        if employee:
            db_session.delete(employee)
    return jsonify({'status': 'success', 'message': 'Employee deleted successfully'})



@app.route("/employees/update/<int:employee_id>", methods=['POST'])
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
def delete_category(cat_id):
    with session_scope() as db_session:
        category = db_session.query(Category).filter(Category.s_no == cat_id).first()
        if category:
            db_session.delete(category)
    return jsonify({'status': 'success', 'message': 'Category deleted successfully'})


@app.route("/categories/update/<int:cat_id>", methods=['POST'])
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
def delete_menu_item(item_id):
    with session_scope() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.s_no == item_id).first()
        if menu_item:
            db_session.delete(menu_item)
    return jsonify({'status': 'success', 'message': 'Menu item deleted successfully'})


@app.route("/menu/update/<int:item_id>", methods=['POST'])
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


@app.route("/status", methods=['GET', 'POST'])
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


app.run(debug=True,host="0.0.0.0")