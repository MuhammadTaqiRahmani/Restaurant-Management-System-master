from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://@DESKTOP-AJ58TNK/DineEase'
db = SQLAlchemy(app)


class Roles(db.Model):
    s_no = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), unique=True)

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
        db.session.add(entry)
        db.session.commit()

    
    
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