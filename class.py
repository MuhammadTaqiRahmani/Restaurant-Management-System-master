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
    __tablename__ = "roles"

    s_no = Column(Integer, primary_key=True, index=True)
    role = Column(String)

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items()))
        
    

Base.metadata.create_all(engine)

class Employees(Base):
    __tablename__ = 'EM'

    s_no = Column(Integer, primary_key=True)
    e_name = Column(String(80))  # Remove unique=True
    e_role = Column(String(80))  # Remove unique=True

    def to_list(self):
        return [self.s_no, self.e_name, self.e_role]
    
    
class Category(Base):
    __tablename__ = 'Category'

    s_no = Column(Integer, primary_key=True)
    cat = Column(String(80), unique=True)

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items()))


    
class Menu(Base):
    __tablename__ = 'Menu'

    s_no = Column(Integer, primary_key=True)
    item = Column(String(80))
    price = Column(Integer)
    status = Column(String(80))
    cat_id = Column(Integer, ForeignKey('Category.s_no'))
    category = relationship("Category", back_populates="menu")

    def to_list(self):
        return [self.s_no, self.item, self.price, self.status, self.cat_id]

# Define the relationship between Category and Menu
Category.menu = relationship("Menu", back_populates="category")

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

# ---------------------------------------------------------------------------------
from flask import redirect, url_for

@app.route("/roles", methods=['GET', 'POST'])
def roles():
    if request.method == 'POST':
        role = request.form.get('role')

        with session_scope() as db_session:
            # Check if the role already exists
            existing_role = db_session.query(Roles).filter(Roles.role == role).first()
            if existing_role is None:
                # If the role does not exist, add it
                entry = Roles(role=role)
                db_session.add(entry)

    # Fetch all roles from the database and order them by s_no in ascending order
    with session_scope() as db_session:
        roles = db_session.query(Roles).options(joinedload('*')).order_by(Roles.s_no).all()
        # Convert roles to a list of dictionaries to ensure it's fully loaded
        roles = [role.to_dict() for role in roles]
        

    return render_template("roles.html", roles=roles)


@app.route("/delete_role", methods=['POST'])
def delete_role():
    if request.method == 'POST':
        role_id = request.form.get('role_id')

        with session_scope() as db_session:
            role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
            if role:
                db_session.delete(role)
                return '', 204  # No Content status code

    return '', 400  # Bad Request status code

@app.route("/edit_role", methods=['POST'])
def edit_role():
    if request.method == 'POST':
        role_id = request.form.get('edit_role_id')
        new_role_name = request.form.get('edit_role')

        with session_scope() as db_session:
            role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
            if role:
                role.role = new_role_name
                db_session.commit()  # Commit the changes to update the existing role
                return '', 204  # No Content status code

    return '', 400  # Bad Request status code


# ---------------------------------------------------------------------------------

@app.route("/employees", methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        e_name = request.form.get('e_name')
        role_id = request.form.get('role_id')  # Corrected variable name
        entry = Employees(e_name=e_name, e_role=role_id)  # Corrected attribute name

        with session_scope() as db_session:
            db_session.add(entry)

    with session_scope() as db_session:
        employees = db_session.query(Employees).order_by(Employees.s_no.asc()).all()
        employees = [employee.to_list() for employee in employees]
        roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
        roles = [role.to_dict() for role in roles]

    return render_template("Employees.html", employees=employees, roles=roles)



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

@app.route("/menu", methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        item = request.form.get('item')
        price = request.form.get('price')
        cat_id = request.form.get('cat_id')
        status = request.form.get('status')

        entry = Menu(item=item, price=price, status=status, cat_id=cat_id)

        with session_scope() as db_session:
            db_session.add(entry)

    with session_scope() as db_session:
        items = (
            db_session.query(Menu)
            .options(joinedload(Menu.category))  # Eager load the category relationship
            .order_by(Menu.s_no.asc())
            .all()
        )
        items = [item.to_list() for item in items]
        categories = db_session.query(Category).order_by(Category.s_no.asc()).all()
        categories = [category.to_dict() for category in categories]

    return render_template("menu.html", items=items, categories=categories)


@app.route("/status")
def status():
    return render_template("status.html")


app.run(debug=True)

