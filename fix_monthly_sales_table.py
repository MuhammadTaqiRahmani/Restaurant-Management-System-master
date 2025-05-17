import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base, MonthlySales, YearlySales
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Get database connection parameters from environment or use defaults
server = os.getenv('DB_SERVER', 'localhost')
database = os.getenv('DB_DATABASE', 'restaurant')
username = os.getenv('DB_USERNAME', 'sa')
password = os.getenv('DB_PASSWORD', 'your_password')

# Connect to database
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
print(f"Connecting to database: {server}/{database}")

engine = create_engine(connection_string, fast_executemany=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_missing_tables():
    """Create only missing tables without dropping existing ones"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Get all table metadata from the Base class
    metadata = Base.metadata
    tables_to_create = []
    
    # Check each table and add to creation list if it doesn't exist
    for table in metadata.sorted_tables:
        if table.name not in existing_tables:
            tables_to_create.append(table)
            print(f"Table {table.name} doesn't exist and will be created.")
    
    # Create only the missing tables
    if tables_to_create:
        print(f"Creating {len(tables_to_create)} missing tables...")
        for table in tables_to_create:
            table.create(engine, checkfirst=True)
        print("Tables created successfully.")
    else:
        print("All tables already exist. No new tables created.")

def initialize_sales_data():
    """Initialize sales data tables with default values"""
    session = SessionLocal()
    try:
        # Check if monthly_sales table has data
        monthly_data_exists = session.query(MonthlySales).first() is not None
        if not monthly_data_exists:
            print("Initializing monthly sales data...")
            # Create data for current year
            current_year = datetime.now().year
            for month in range(1, 13):
                monthly_sales = MonthlySales(
                    year=current_year,
                    month=month,
                    total_sales=0.0,
                    order_count=0
                )
                session.add(monthly_sales)
            
            # Create data for previous year
            prev_year = current_year - 1
            for month in range(1, 13):
                monthly_sales = MonthlySales(
                    year=prev_year,
                    month=month,
                    total_sales=0.0,
                    order_count=0
                )
                session.add(monthly_sales)
        else:
            print("Monthly sales data already exists.")
            
        # Check if yearly_sales table has data
        yearly_data_exists = session.query(YearlySales).first() is not None
        if not yearly_data_exists:
            print("Initializing yearly sales data...")
            # Create records for current and previous years
            current_year = datetime.now().year
            years_to_add = [current_year - 1, current_year]
            
            for year in years_to_add:
                yearly_sales = YearlySales(
                    year=year,
                    total_sales=0.0,
                    order_count=0
                )
                session.add(yearly_sales)
        else:
            print("Yearly sales data already exists.")
            
        session.commit()
        print("Sales data initialization complete.")
    except Exception as e:
        session.rollback()
        print(f"Error initializing sales data: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    # Check for monthly_sales table
    if check_table_exists('monthly_sales'):
        print("The monthly_sales table already exists.")
    else:
        print("The monthly_sales table doesn't exist. Creating it now...")
        
    # Create only missing tables without affecting existing ones
    create_missing_tables()
    
    # Initialize sales data
    initialize_sales_data()
    
    print("Fix complete. The /months route should now work correctly.")