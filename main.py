from flask import Flask,render_template,request, jsonify
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from models import Roles, Employees, Category, Menu, Status, Order
from database import Base, engine, session_scope

app = Flask(__name__)

Base.metadata.create_all(engine)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chart")
def chartjs():
    return render_template("chartjs.html")

@app.route("/table")
def table():
    return render_template("basic-table.html")


@app.route("/management")
def management():
    return render_template("Managementib.html")

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

# ---------------------------------------------------------------------------------
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

        with session_scope() as db_session:
            db_session.add(entry)

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
        category = db_session.query(Category).filter(Category.s_no == cat_id).first()
        if category:
            category.cat = cat_name
            db_session.add(category)
    return jsonify({'status': 'success', 'message': 'Category updated successfully'})


@app.route("/menu", methods=['GET', 'POST'])
def menu():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        CategoryAlias = aliased(Category)

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
            entry = Status(floor=floor,category=category ,customer=customer,table_no=table_no)
            db_session.add(entry)

    with session_scope() as db_session:
        statuses = db_session.query(Status).order_by(Status.s_no.asc()).all()
        statuses = [status.to_list() for status in statuses]
        
    return render_template("status.html", statuses=statuses)



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
        o_customer_id = request.form.get('o_customer_id')
        o_item = request.form.get('o_item')
        amountOfItems = int(request.form.get('amountOfItems'))
        bill = int(request.form.get('bill'))

        with session_scope() as db_session:
            entry = Order(o_customer_id=o_customer_id, o_item=o_item, amountOfItems=amountOfItems, bill=bill)
            db_session.add(entry)

    with session_scope() as db_session:
        orders = db_session.query(
            Order.s_no, 
            Status.floor, 
            Status.table_no, 
            Order.o_item, 
            Order.amountOfItems, 
            Order.bill
        ).join(Status, Order.o_customer_id == Status.s_no).order_by(Order.s_no.asc()).all()
        
        status = db_session.query(Status).order_by(Status.s_no.asc()).all()
        status = [s.to_list() for s in status]

    return render_template("orders.html", orders=orders, status=status)

app.run(debug=True,host="0.0.0.0")