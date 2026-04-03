# Import necessary libraries
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy import UniqueConstraint

# Class to declare the base model.
class Base(DeclarativeBase):
    pass

# Class to represent the product which is present in the tenant db
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Class to declare the product base model shcema
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sub_category_id = Column(Integer)     
    name = Column(String(255))
    title = Column(String(255))
    mrp = Column(Float)              
    special_price = Column(Float)
    stock_count = Column(Integer)
    stock_status = Column(String(50))
    created_at = Column(DateTime)
    image_url = Column(String(500))


# Class to represent the wishlist which is present in the tenant db
class Wishlist(Base):
    __tablename__ = "wishlist"
    __table_args__ = (
        UniqueConstraint('product_id', 'user_session', name='uq_wishlist_product_session'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_session = Column(String(255), default="demo_session")
    created_at = Column(DateTime)

#  Class to represent the order which is present in the tenant db
class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = (
        UniqueConstraint('product_id', 'user_session', name='uq_cart_product_session'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_session = Column(String(255), default="demo_session")
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

# Function to create the orders tables based on the shcema.
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True)
    user_session = Column(String(255))
    subtotal = Column(Float)
    tax = Column(Float)
    grand_total = Column(Float)
    status = Column(String(50), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

# Function to create the table for the order items.
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    title = Column(String(255))
    quantity = Column(Integer)
    price = Column(Float)
    total = Column(Float)
