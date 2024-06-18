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
@app.route("/roles", methods = ['GET','POST'])
def roles():
    if (request.method=='POST'):
        '''Add entry to database'''
        role =  request.form.get('role')     
        entry = Roles(role=role)

        # Create a new session
        db_session = SessionLocal()

        # Add the new entry and commit the changes
        db_session.add(entry)
        db_session.commit()

        # Close the session
        db_session.close()

    return render_template("roles.html")

@app.route("/employees")
def users():
    return render_template("Employees.html")

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