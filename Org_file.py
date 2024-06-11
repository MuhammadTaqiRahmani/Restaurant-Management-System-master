from flask import Flask,render_template,request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask import Flask
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy.orm import joinedload
from contextlib import contextmanager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from flask import jsonify

app = Flask(__name__)

# Define the database connection parameters
server = 'DESKTOP-AJ58TNK'
database = 'DineEase'
driver = '{ODBC Driver 17 for SQL Server}'

# Create the engine
engine = create_engine(
    f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
    fast_executemany=True)

# Create a base class for the models
Base = declarative_base()

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db_session = SessionLocal()
    try:
        yield db_session
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

# Define the Roles model
class Roles(Base):
    __tablename__ = "rolesTestDine"

    s_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String(255), unique=True)  # Change this line

    employees = relationship("Employees", back_populates="role")

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items())) 

class Employees(Base):
    __tablename__ = 'employeesTestDine'

    s_no = Column(Integer, primary_key=True, autoincrement=True)
    e_name = Column(String(80))
    e_role = Column(Integer, ForeignKey('rolesTestDine.s_no'))

    role = relationship("Roles", back_populates="employees")

    def to_list(self):
        return [self.s_no, self.e_name, self.e_role]

class Category(Base):
    __tablename__ = 'categoriesTestDine'

    s_no = Column(Integer, primary_key=True, autoincrement=True)
    cat = Column(String(80), unique=True)

    menu = relationship("Menu", back_populates="category_rel")

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items())) 

class Menu(Base):
    __tablename__ = 'menuTestDine'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(String(80),unique=True)
    price = Column(Integer)
    category = Column(Integer, ForeignKey('categoriesTestDine.s_no'))
    status = Column(String(80))

    category_rel = relationship("Category", back_populates="menu")

    def to_list(self):
        return [self.s_no, self.item, self.price, self.category_rel.cat, self.status]

# Define the Status model
# Define the Status model
class Status(Base):
    __tablename__ = 'statusTestDine'
    
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    floor = Column(String(80))  # Add floor column
    category = Column(String(80))
    customer = Column(Integer)  # Add customer column
    table_no = Column(Integer)
    


    def to_list(self):
        return [self.s_no, self.floor,self.category,self.customer,self.table_no]

    
# class Order(Base):
#     __tablename__ = 'orderTestDine'
    
#     o_customer_id = Column(Integer, ForeignKey('statusTestDine.s_no'))
#     o_item = Column(String(80))
#     amountOfItems = Column(Integer)
#     bill = Column(Integer)
    
#     status = relationship("Status", back_populates="order")
    
#     def to_list(self):
#         return [self.o_customer_id, self.o_item,self.amountOfItems,self.bill]
    

Base.metadata.create_all(engine)


# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    return render_template("management.html")

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
        role_name = request.form.get('role_id')  # Get role name

        with session_scope() as db_session:
            role = db_session.query(Roles).filter(Roles.role == role_name).first()  # Query role by name
            if role:
                entry = Employees(e_name=e_name, e_role=role.s_no)  # Use role's s_no
                db_session.add(entry)
            else:
                return jsonify({'status': 'error', 'message': 'Role not found'}), 400

    with session_scope() as db_session:
        # Join Employees and Roles tables and select necessary fields
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
    emp_role_name = request.form.get('edit_role')  # Get role name

    with session_scope() as db_session:
        role = db_session.query(Roles).filter(Roles.role == emp_role_name).first()  # Query role by name
        if role:
            employee = db_session.query(Employees).filter(Employees.s_no == employee_id).first()
            if employee:
                employee.e_name = emp_name
                employee.e_role = role.s_no  # Use role's s_no
                db_session.add(employee)
    return jsonify({'status': 'success', 'message': 'Employee updated successfully'})


# ---------------------------------------------------------------------------------


@app.route("/categories", methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        cat = request.form.get('cat')
        entry = Category(cat=cat)

        with session_scope() as db_session:
            db_session.add(entry)

    # Fetch all categories from the database and order them by s_no in ascending order
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


# ---------------------------------------------------------------------------------
@app.route("/menu", methods=['GET', 'POST'])
def menu():
    try:
        # Create a new session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create an alias for the Category table
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


        # Convert each item to a dictionary and replace the category id with the category name
        items = [item.to_list() for item in items]
        categories = session.query(Category).order_by(Category.s_no.asc()).all()
        categories = [category.to_dict() for category in categories]

        print(f"Items: {items}")  # Print items
        print(f"Categories: {categories}")  # Print categories

        session.close()  # Close the session

        return render_template("menu.html", items=items, categories=categories)
    except Exception as e:
        print(f"Error: {e}")  # Print any exceptions
        return str(e), 500  # Return the error message and a 500 status code



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
            
            # Fetch the category name using the provided cat_id
            category_obj = db_session.query(Category).filter(Category.s_no == cat_id).first()
            if category_obj:
                menu_item.category = cat_id  # Store the category ID
            
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

# ---------------------------------------------------------------------------------

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






app.run(debug=True,host="0.0.0.0")