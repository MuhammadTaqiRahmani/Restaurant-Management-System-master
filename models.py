import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Boolean, Float, Date, func, extract
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash

# creation of models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime, default=datetime.datetime.utcnow)
    employee_id = Column(Integer, ForeignKey('employeesTestDine.s_no'), nullable=True)
    employee = relationship("Employees", foreign_keys=[employee_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'date_joined': self.date_joined,
            'employee_id': self.employee_id
        }

class Roles(Base):
    __tablename__ = "rolesTestDine"
    s_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String(255), unique=True)  
    employees = relationship("Employees", back_populates="role", cascade="all, delete-orphan")

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items())) 

class Employees(Base):
    __tablename__ = 'employeesTestDine'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    e_name = Column(String(80))
    e_role = Column(Integer, ForeignKey('rolesTestDine.s_no'))
    role = relationship("Roles", back_populates="employees")

    def to_list(self):
        return [self.s_no, self.e_name, self.e_role]

class Category(Base):
    __tablename__ = 'categoriesTestDine'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    cat = Column(String(80), unique=True)
    menu = relationship("Menu", back_populates="category_rel")

    def to_dict(self):
        unsorted_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return dict(sorted(unsorted_dict.items())) 

class Menu(Base):
    __tablename__ = 'menuTestDine'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(String(80), unique=True, index=True)
    price = Column(Integer)
    category = Column(Integer, ForeignKey('categoriesTestDine.s_no'))
    status = Column(String(80))
    category_rel = relationship("Category", back_populates="menu")
    order_items = relationship("OrderItem", back_populates="menu_item")

    def to_list(self):
        return [self.s_no, self.item, self.price, self.category_rel.cat, self.status]

class Status(Base):
    __tablename__ = 'statusTestDine'
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    floor = Column(String(80))  
    category = Column(String(80))
    customer = Column(Integer)  
    table_no = Column(Integer)
    orders = relationship("Order", back_populates="status")

    def to_list(self):
        return [self.s_no, self.floor, self.category, self.customer, self.table_no]


class OrderItem(Base):
    __tablename__ = 'order_items'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    menu_item_id = Column(Integer, ForeignKey('menuTestDine.s_no'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("Menu", back_populates="order_items")

class Order(Base):
    __tablename__ = 'orders'
    date = Column(DateTime, default=datetime.datetime.utcnow)
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_status_id = Column(Integer, ForeignKey('statusTestDine.s_no'), index=True)
    status = relationship("Status", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    bill = relationship("Bill", back_populates="order", uselist=False)  # Add this line

class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    total = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="bill")  # Ensure this line is correct
    time = Column(DateTime, default=datetime.datetime.utcnow)
    
    # for bill calculation
    def calculate_total(self):
        self.total = sum(item.menu_item.price * item.quantity for item in self.order.items)
        return self.total

class MonthlySales(Base):
    __tablename__ = 'monthly_sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12 for Jan-Dec
    total_sales = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'total_sales': self.total_sales,
            'order_count': self.order_count,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def get_month_name(cls, month_number):
        months = ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
        return months[month_number - 1] if 1 <= month_number <= 12 else "Unknown"

class YearlySales(Base):
    __tablename__ = 'yearly_sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, unique=True)
    total_sales = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'total_sales': self.total_sales,
            'order_count': self.order_count,
            'updated_at': self.updated_at
        }