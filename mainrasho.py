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

# Define the Roles model
class Roles(Base):
    __tablename__ = 'Roles'

    s_no = Column(Integer, primary_key=True)
    role = Column(String(80), unique=True)
    
    

Base.metadata.create_all(engine)

class Employees(Base):
    __tablename__ = 'EM'

    s_no = Column(Integer, primary_key=True)
    e_name = Column(String(80))  # Remove unique=True
    e_role = Column(String(80))  # Remove unique=True
    
    
class Category(Base):
    __tablename__ = 'Category'

    s_no = Column(Integer, primary_key=True)
    cat = Column(String(80), unique=True)


    
class Menu(Base):
    __tablename__ = 'Menu'

    s_no = Column(Integer, primary_key=True)
    item = Column(String(80))
    price = Column(Integer)
    status = Column(String(80))
    cat_id = Column(Integer, ForeignKey('Category.s_no'))
    category = relationship("Category", back_populates="menu")

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
        entry = Roles(role=role)

        db_session = SessionLocal()
        db_session.add(entry)
        db_session.commit()
        db_session.close()

    # Fetch all roles from the database and order them by s_no in ascending order
    db_session = SessionLocal()
    roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
    db_session.close()

    return render_template("roles.html", roles=roles)


@app.route("/delete_role", methods=['POST'])
def delete_role():
    if request.method == 'POST':
        role_id = request.form.get('role_id')

        db_session = SessionLocal()
        role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
        if role:
            db_session.delete(role)
            db_session.commit()
        db_session.close()

    return redirect(url_for('roles'))





@app.route("/employees", methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        e_name = request.form.get('e_name')
        role_id = request.form.get('role_id')  # Corrected variable name
        entry = Employees(e_name=e_name, e_role=role_id)  # Corrected attribute name

        db_session = SessionLocal()
        db_session.add(entry)
        db_session.commit()
        db_session.close()

    db_session = SessionLocal()
    employees = db_session.query(Employees).order_by(Employees.s_no.asc()).all()
    roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
    db_session.close()

    print(roles)
    return render_template("Employees.html", employees=employees, roles=roles)




@app.route("/categories", methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        cat = request.form.get('cat')
        entry = Category(cat=cat)

        db_session = SessionLocal()
        db_session.add(entry)
        db_session.commit()
        db_session.close()

    # Fetch all categories from the database and order them by s_no in ascending order
    db_session = SessionLocal()
    cats = db_session.query(Category).order_by(Category.s_no.asc()).all()
    db_session.close()

    return render_template("foodCategories.html", cats=cats)

        





@app.route("/menu", methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        item = request.form.get('item')
        price = request.form.get('price')
        cat_id = request.form.get('cat_id')
        status = request.form.get('status')
        
        entry = Menu(item=item, price=price, status=status, cat_id=cat_id)

        db_session = SessionLocal()
        db_session.add(entry)
        db_session.commit()
        db_session.close()

    db_session = SessionLocal()
    items = (
        db_session.query(Menu)
        .options(joinedload(Menu.category))  # Eager load the category relationship
        .order_by(Menu.s_no.asc())
        .all()
    )
    categories = db_session.query(Category).order_by(Category.s_no.asc()).all()
    db_session.close()
    
    return render_template("menu.html", items=items, categories=categories)



@app.route("/status")
def status():
    return render_template("status.html")


app.run(debug=True)