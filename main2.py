# from flask import Flask,render_template,request
# from flask_sqlalchemy import SQLAlchemy


# app = Flask(__name__)

# # app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://username:password@localhost/db_name'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://@DESKTOP-AJ58TNK/DineEase'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+asyncmy://root:@DESKTOP-AJ58TNK/DineEase?'

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql//@DESKTOP-AJ58TNK/DineEase'
# db = SQLAlchemy(app)


# class Roles(db.Model):
#     s_no = db.Column(db.Integer, primary_key=True)
#     role = db.Column(db.String(80), unique=True)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chart")
# def chartjs():
#     return render_template("chartjs.html")

# @app.route("/table")
# def table():
#     return render_template("basic-table.html")


# @app.route("/management")
# def management():
#     return render_template("management.html")

# # ---------------------------------------------------------------------------------
# @app.route("/roles", methods = ['GET','POST'])
# def roles():
#     if (request.method=='POST'):
#         '''Add entry to database'''
#         role =  request.form.get('role')     
#         entry = Roles(role=role)
#         db.session.add(entry)
#         db.session.commit()

    
    
#     return render_template("roles.html")

# @app.route("/employees")
# def users():
#     return render_template("Employees.html")

# @app.route("/categories")
# def categories():
#     return render_template("foodCategories.html")

# @app.route("/menu")
# def menu():
#     return render_template("menu.html")

# @app.route("/status")
# def status():
#     return render_template("status.html")


# app.run(debug=True)
































from flask import Flask,render_template,request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from flask import Flask
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
    __tablename__ = 'employees222'

    s_no = Column(Integer, primary_key=True)
    e_name = Column(String(80))  # Remove unique=True
    e_role = Column(String(80))  # Remove unique=True



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

    return render_template("Employees.html", employees=employees, roles=roles)





@app.route("/categories")
def categories():
    return render_template("foodCategories.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/status")
def status():
    return render_template("status.html")


app.run(debug=True)