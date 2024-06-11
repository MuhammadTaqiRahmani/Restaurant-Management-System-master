from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Roles(Base):
    __tablename__ = "rolesTestDine"

    s_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(String(255), unique=True)  

    employees = relationship("Employees", back_populates="role")

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
    item = Column(String(80),unique=True)
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
    
    order = relationship("Order", back_populates="status")

    def to_list(self):
        return [self.s_no, self.floor, self.category, self.customer, self.table_no]


    
class Order(Base):
    __tablename__ = 'orderTestDine'
    
    s_no = Column(Integer, primary_key=True, autoincrement=True)
    o_customer_id = Column(Integer, ForeignKey('statusTestDine.s_no'))
    o_item = Column(String(80), ForeignKey('menuTestDine.item'))
    amountOfItems = Column(Integer)
    bill = Column(Integer)
    
    status = relationship("Status", back_populates="order", foreign_keys=[o_customer_id])
    item_details = relationship("Menu", foreign_keys=[o_item])

    def to_list(self):
        return [self.s_no, self.o_customer_id, self.status.floor, self.status.table_no, self.o_item, self.amountOfItems, self.bill]