
# Restaurant Management System

The Restaurant Management System is a comprehensive web application designed to streamline the
daily operations of a restaurant. This system, built using the Flask framework, aims to provide a holistic
solution for managing orders, menu items, inventory, employees, and customer relations. Enhanced
with real-time data visualization using Chart.js, it enables restaurant managers to make informed
decisions based on sales trends and profit analysis.


## Project Objectives
* Efficiency: To create a user-friendly interface that simplifies restaurant operations.
* Data-Driven Decisions: To provide real-time insights into sales and profits.
* Customer Satisfaction: To improve the dining experience through       efficient order and service management.
* Resource Management: To optimize inventory and staff management.

## System Architecture
* Model: Represents the data structure. The database interactions and business logic are handled here.
* View: The user interface components. It displays data to the user and sends user commands to the controller.
* Controller: Acts as an intermediary between the Model and View. It processes user input, manipulates data, and updates the view.

## Models Overview
#### Order Management

* Description: Handles customer orders, tracks their status, and manages table assignments.
* Features: Order placement, status tracking, table management.

#### Menu Management
* Description: Manages the restaurant’s menu, including item descriptions, prices, and availability.
* Features: Add, update, delete menu items, categorize items.


#### Inventory Control
* Description: Monitors and manages inventory levels to ensure the kitchen is stocked.
* Features: Inventory tracking, stock alerts, supplier management.

#### Sales Analytics
* Description: Uses Chart.js to visualize sales trends and profit margins.
* Features: Sales reports, profit analysis, trend visualization.

#### Employee Management
* Description: Manages staff schedules, roles, and payroll.
* Features: Schedule creation, role assignment, payroll management.

#### Customer Relationship Management
* Description: Tracks customer preferences and feedback.
* Features: Customer profiles, feedback collection, loyalty programs.

## Technologies Used
### Backend
* Framework: [Flask](https://flask.palletsprojects.com/en/3.0.x/) (Python)
* Server: Gunicorn (optional)

### Frontend
* Languages: [HTML](https://www.w3schools.com/html/), [CSS](https://www.w3schools.com/css/), [JavaScript](https://www.w3schools.com/js/DEFAULT.asp)
* Frameworks/Libraries: [Bootstrap](https://getbootstrap.com/), [jQuery](https://jquery.com/)

### Database
* Options: [MS SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-downloads).

### Data Visualization
* Library: [Chart.js](https://www.chartjs.org/)

## Packages and Libraries

* Flask: Web framework for building the application.
* SQLAlchemy: ORM for database interactions.
* WTForms: Form handling and validation.
* Flask-Login: User session management.
* Flask-Migrate: Database migrations.
* Jinja2: Templating engine for rendering HTML.
* Chart.js: JavaScript library for data visualization.
* Bootstrap: Frontend framework for responsive design.
* jQuery: JavaScript library for DOM manipulation.
* pyodbc: Python library for connecting to ODBC databases.

## Database Models

* Roles
* Employees
* Category
* Menu
* Bill
* Bill Calculation Method














## USER GUIDE

### System Requirements
* Operating System: Windows, macOS, or Linux
* Browser: Latest versions of Chrome, Firefox, Safari, or Edge
* Python: Version 3.7 or higher
* Database: MS SQL Server

### Installation

#### Clone the Repository

```bash
  git clone https://github.com/MuhammadTaqiRahmani/Resturant-Management-System-master.git
```

#### Navigate to the Project Directory

```bash
  cd Resturant-Management-System-master
```

#### Create a Virtual Environment

```bash
  python -m venv venv
```

#### Activate the Virtual Environment

* On Windows
```bash
  venv\Scripts\activate
```

* On macos/Linux
```bash
  source venv/bin/activate
```

#### Install Dependencies
```bash
  pip install -r requirements.txt
```

#### Run the Application
```bash
  python main.py
```

