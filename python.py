# import pymssql

# # Connect to the database
# conn = pymssql.connect(server='DESKTOP-AJ58TNK', database='DineEase')

# # Create a cursor object to execute queries
# cursor = conn.cursor()

# # Example query execution (selecting data)
# cursor.execute('SELECT * FROM Roles123')

# # Fetch data
# rows = cursor.fetchall()

# # Process fetched data
# for row in rows:
#     print(row)

# # Close cursor and connection
# cursor.close()
# conn.close()



# import pyodbc

# server = 'DESKTOP-AJ58TNK' 
# database = 'DineEase' 
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
# cursor = cnxn.cursor()


import pyodbc

server = 'DESKTOP-AJ58TNK'
database = 'DineEase'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
cursor = cnxn.cursor()

# Define a query to select all data from Roles123 table
sql_query = "SELECT * FROM Roles123"

# Execute the query
cursor.execute(sql_query)

# Fetch all results at once
all_data = cursor.fetchall()

# Print the data row by row
for row in all_data:
  print(row)

# Close the cursor and connection
cursor.close()
cnxn.close()




# from flask import Flask,render_template,request
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# from flask import Flask
# from flask import Flask, render_template, request
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# app = Flask(__name__)

# # Define the database connection parameters
# server = 'DESKTOP-AJ58TNK'
# database = 'DineEase'
# driver = '{ODBC Driver 17 for SQL Server}'

# # Create the engine
# engine = create_engine(
#     f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
#     fast_executemany=True)

# # Create a base class for the models
# Base = declarative_base()

# # Create a session factory bound to the engine
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Define the Roles model
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship

# class Roles(Base):
#     __tablename__ = 'Roles'

#     s_no = Column(Integer, primary_key=True)
#     role = Column(String(80), unique=True)
    
#     # Define a relationship between Roles and Employees
#     employees = relationship("Employees", back_populates="role")

# class Employees(Base):
#     __tablename__ = 'employees8'

#     s_no = Column(Integer, primary_key=True)
#     e_name = Column(String(80))
    
#     # Add a foreign key to link to the Roles table
#     e_role_s_no = Column(Integer, ForeignKey('Roles.s_no'))
    
#     # Define the relationship between Employees and Roles
#     role = relationship("Roles", back_populates="employees")




# Base.metadata.create_all(engine)
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
# @app.route("/roles", methods=['GET', 'POST'])
# def roles():
#     if request.method == 'POST':
#         role = request.form.get('role')
#         entry = Roles(role=role)

#         db_session = SessionLocal()
#         db_session.add(entry)
#         db_session.commit()
#         db_session.close()

#     # Fetch all roles from the database and order them by s_no in ascending order
#     db_session = SessionLocal()
#     roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
#     db_session.close()

#     return render_template("roles.html", roles=roles)


# @app.route("/employees", methods=['GET', 'POST'])
# def employee():
#     if request.method == 'POST':
#         e_name = request.form.get('e_name')
#         role_name = request.form.get('role_name')  # Retrieve the selected role name from the form
#         print("Selected Role Name:", role_name)  # Print the selected role name for debugging

#         db_session = SessionLocal()

#         # Fetch the role object based on the selected role name
#         role = db_session.query(Roles).filter(Roles.role == role_name).first()

#         if role:
#             # If the role exists, create a new employee object with the retrieved role_s_no
#             entry = Employees(e_name=e_name, e_role=role.s_no)

#             db_session.add(entry)
#             db_session.commit()
#             db_session.close()

#     db_session = SessionLocal()
#     employees = db_session.query(Employees).order_by(Employees.s_no.asc()).all()
#     roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
#     db_session.close()

#     return render_template("Employees.html", employees=employees, roles=roles)










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


# -----------------------------------------------------------------------------
# from flask import Flask,render_template,request
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# from flask import Flask
# from flask import Flask, render_template, request
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# app = Flask(__name__)

# # Define the database connection parameters
# server = 'DESKTOP-AJ58TNK'
# database = 'DineEase'
# driver = '{ODBC Driver 17 for SQL Server}'

# # Create the engine
# engine = create_engine(
#     f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server",
#     fast_executemany=True)

# # Create a base class for the models
# Base = declarative_base()

# # Create a session factory bound to the engine
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Define the Roles model
# class Roles(Base):
#     __tablename__ = 'Roles'

#     s_no = Column(Integer, primary_key=True)
#     role = Column(String(80), unique=True)
    
    

# Base.metadata.create_all(engine)

# class Employees(Base):
#     __tablename__ = 'employeesC'

#     s_no = Column(Integer, primary_key=True)
#     e_name = Column(String(80))  # Remove unique=True
#     e_role = Column(String(80))  # Remove unique=True



# Base.metadata.create_all(engine)
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
# @app.route("/roles", methods=['GET', 'POST'])
# def roles():
#     if request.method == 'POST':
#         role = request.form.get('role')
#         entry = Roles(role=role)

#         db_session = SessionLocal()
#         db_session.add(entry)
#         db_session.commit()
#         db_session.close()

#     # Fetch all roles from the database and order them by s_no in ascending order
#     db_session = SessionLocal()
#     roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
#     db_session.close()

#     return render_template("roles.html", roles=roles)



# @app.route("/employees", methods=['GET', 'POST'])
# def employee():
#     if request.method == 'POST':
#         e_name = request.form.get('e_name')
#         role_name = request.form.get('role_name')  # Retrieve the selected role name from the form
#         print("Selected Role Name:", role_name)  # Print the selected role name for debugging

#         db_session = SessionLocal()

#         # Fetch the role object based on the selected role name
#         role = db_session.query(Roles).filter(Roles.role == role_name).first()

#         if role:
#             # If the role exists, create a new employee object with the retrieved role_s_no
#             entry = Employees(e_name=e_name, role=role)

#             db_session.add(entry)
#             db_session.commit()
#             db_session.close()

                    
#     db_session = SessionLocal()
#     employees = db_session.query(Employees).order_by(Employees.s_no.asc()).all()
#     roles = db_session.query(Roles).order_by(Roles.s_no.asc()).all()
#     db_session.close()

#     return render_template("Employees.html", employees=employees, roles=roles)






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




















# @app.route("/edit_role", methods=['POST'])
# def edit_role():
#     if request.method == 'POST':
#         role_id = request.form.get('role_id')
#         role_name = request.form.get('role')

#         db_session = SessionLocal()
#         role = db_session.query(Roles).filter(Roles.s_no == role_id).first()
#         if role:
#             role.role = role_name  # Update role name
#             db_session.commit()
#         db_session.close()

#     return redirect(url_for('roles'))
