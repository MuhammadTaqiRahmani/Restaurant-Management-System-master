import datetime
from sqlalchemy import extract, func
from models import Bill, MonthlySales, YearlySales
from database import session_scope

def update_monthly_sales(bill_total, bill_time=None):
    """
    Update the monthly sales after a new bill is created.
    
    Args:
        bill_total (float): The total amount from the bill
        bill_time (datetime, optional): The timestamp of the bill. Defaults to current time.
    """
    if bill_time is None:
        bill_time = datetime.datetime.now()
    
    year = bill_time.year
    month = bill_time.month
    
    with session_scope() as db_session:
        # Check if we already have an entry for this month/year
        monthly_sales = db_session.query(MonthlySales).filter(
            MonthlySales.year == year,
            MonthlySales.month == month
        ).first()
        
        if monthly_sales:
            # Update existing record
            monthly_sales.total_sales += bill_total
            monthly_sales.order_count += 1
        else:
            # Create new record
            monthly_sales = MonthlySales(
                year=year,
                month=month,
                total_sales=bill_total,
                order_count=1
            )
            db_session.add(monthly_sales)

def update_yearly_sales(bill_total, bill_time=None):
    """
    Update the yearly sales after a new bill is created.
    
    Args:
        bill_total (float): The total amount from the bill
        bill_time (datetime, optional): The timestamp of the bill. Defaults to current time.
    """
    if bill_time is None:
        bill_time = datetime.datetime.now()
    
    year = bill_time.year
    
    with session_scope() as db_session:
        # Check if we already have an entry for this year
        yearly_sales = db_session.query(YearlySales).filter(
            YearlySales.year == year
        ).first()
        
        if yearly_sales:
            # Update existing record
            yearly_sales.total_sales += bill_total
            yearly_sales.order_count += 1
        else:
            # Create new record
            yearly_sales = YearlySales(
                year=year,
                total_sales=bill_total,
                order_count=1
            )
            db_session.add(yearly_sales)

def get_monthly_sales_data(year=None):
    """
    Get monthly sales data for a specific year.
    
    Args:
        year (int, optional): The year to get data for. Defaults to current year.
    
    Returns:
        list: List of dictionaries containing monthly sales data
    """
    if year is None:
        year = datetime.datetime.now().year
    
    with session_scope() as db_session:
        monthly_sales = db_session.query(MonthlySales).filter(
            MonthlySales.year == year
        ).order_by(MonthlySales.month).all()
        
        # Format data for chart display
        result = []
        for ms in monthly_sales:
            result.append({
                'month': MonthlySales.get_month_name(ms.month),
                'month_num': ms.month,
                'total_sales': ms.total_sales,
                'order_count': ms.order_count
            })
        
        return result

def get_yearly_sales_data(start_year=None, end_year=None):
    """
    Get yearly sales data.
    
    Args:
        start_year (int, optional): Start year. Defaults to 5 years ago.
        end_year (int, optional): End year. Defaults to current year.
    
    Returns:
        list: List of dictionaries containing yearly sales data
    """
    current_year = datetime.datetime.now().year
    
    if start_year is None:
        start_year = current_year - 5
    
    if end_year is None:
        end_year = current_year
    
    with session_scope() as db_session:
        yearly_sales = db_session.query(YearlySales).filter(
            YearlySales.year >= start_year,
            YearlySales.year <= end_year
        ).order_by(YearlySales.year).all()
        
        # Format data for chart display
        result = []
        for ys in yearly_sales:
            result.append({
                'year': ys.year,
                'total_sales': ys.total_sales,
                'order_count': ys.order_count
            })
        
        return result

def process_historical_sales_data():
    """
    Calculate monthly and yearly sales from historical bill data.
    This should be run once to populate the sales tables from existing bills.
    """
    with session_scope() as db_session:
        # First, clear existing data
        db_session.query(MonthlySales).delete()
        db_session.query(YearlySales).delete()
        
        # Get monthly aggregates
        monthly_data = db_session.query(
            extract('year', Bill.time).label('year'),
            extract('month', Bill.time).label('month'),
            func.sum(Bill.total).label('total_sales'),
            func.count(Bill.id).label('order_count')
        ).group_by(
            extract('year', Bill.time),
            extract('month', Bill.time)
        ).all()
        
        # Insert monthly records
        for year, month, total_sales, order_count in monthly_data:
            monthly_sales = MonthlySales(
                year=int(year),
                month=int(month),
                total_sales=float(total_sales),
                order_count=int(order_count)
            )
            db_session.add(monthly_sales)
            
        # Get yearly aggregates
        yearly_data = db_session.query(
            extract('year', Bill.time).label('year'),
            func.sum(Bill.total).label('total_sales'),
            func.count(Bill.id).label('order_count')
        ).group_by(
            extract('year', Bill.time)
        ).all()
        
        # Insert yearly records
        for year, total_sales, order_count in yearly_data:
            yearly_sales = YearlySales(
                year=int(year),
                total_sales=float(total_sales),
                order_count=int(order_count)
            )
            db_session.add(yearly_sales)