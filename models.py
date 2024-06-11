from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint
from database import Base

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


    
class Order(Base):
    __tablename__ = 'orderTestDine'
    
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    customer_status_id = Column(Integer, ForeignKey('statusTestDine.s_no'), index=True)
    menu_item = Column(String(80), ForeignKey('menuTestDine.item'), index=True) 
    amountOfItems = Column(Integer, CheckConstraint('amountOfItems>=0')) 
    bill = Column(Integer, CheckConstraint('bill>=0'))
    
    status = relationship("Status", back_populates="orders", foreign_keys=[customer_status_id])
    item_details = relationship("Menu", foreign_keys=[menu_item], cascade="all, delete")  # Added cascade option

    def to_list(self):
        return [self.s_no, self.customer_status_id, self.status.floor, self.status.table_no, self.menu_item, self.amountOfItems, self.bill]