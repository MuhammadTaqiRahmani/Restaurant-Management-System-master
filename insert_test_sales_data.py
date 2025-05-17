from database import session_scope
from models import MonthlySales, YearlySales
import datetime
import random

def insert_test_sales_data():
    """
    Insert test data into the monthly_sales and yearly_sales tables.
    This is for testing the sales visualization on the dashboard.
    """
    print("Inserting test sales data...")
    
    current_year = datetime.datetime.now().year
    
    # Sample data for the last 3 years
    years_to_create = [current_year - 2, current_year - 1, current_year]
    
    with session_scope() as db_session:
        # First clear existing data (optional - uncomment if you want to start fresh)
        # db_session.query(MonthlySales).delete()
        # db_session.query(YearlySales).delete()
        
        # Create yearly sales data
        for year in years_to_create:
            # Check if yearly record already exists
            existing_yearly = db_session.query(YearlySales).filter(YearlySales.year == year).first()
            
            yearly_total = random.randint(500000, 1500000)  # Random total between 500,000 and 1,500,000
            yearly_orders = random.randint(5000, 15000)     # Random order count
            
            if existing_yearly:
                existing_yearly.total_sales = yearly_total
                existing_yearly.order_count = yearly_orders
                existing_yearly.updated_at = datetime.datetime.now()
            else:
                yearly_sales = YearlySales(
                    year=year,
                    total_sales=yearly_total,
                    order_count=yearly_orders,
                    updated_at=datetime.datetime.now()
                )
                db_session.add(yearly_sales)
            
            # Create monthly sales data for each year
            for month in range(1, 13):
                # Generate more realistic data pattern (higher in certain months)
                if month in [3, 6, 9, 12]:  # Quarterly peaks
                    monthly_total = random.randint(80000, 150000)
                    monthly_orders = random.randint(800, 1500)
                elif month in [1, 2]:  # Slow start of year
                    monthly_total = random.randint(30000, 70000)
                    monthly_orders = random.randint(300, 700)
                else:  # Regular months
                    monthly_total = random.randint(50000, 100000)
                    monthly_orders = random.randint(500, 1000)
                
                # Check if monthly record already exists
                existing_monthly = db_session.query(MonthlySales).filter(
                    MonthlySales.year == year,
                    MonthlySales.month == month
                ).first()
                
                if existing_monthly:
                    existing_monthly.total_sales = monthly_total
                    existing_monthly.order_count = monthly_orders
                    existing_monthly.updated_at = datetime.datetime.now()
                else:
                    monthly_sales = MonthlySales(
                        year=year,
                        month=month,
                        total_sales=monthly_total,
                        order_count=monthly_orders,
                        updated_at=datetime.datetime.now()
                    )
                    db_session.add(monthly_sales)
        
        db_session.commit()
        print("Test sales data inserted successfully!")
        print(f"Created data for years: {years_to_create}")
        print(f"Created monthly data for all 12 months in each year")

if __name__ == "__main__":
    insert_test_sales_data()