# backend/app/models/__init__.py
"""
Database models for the Grocery Voice App.

This package contains SQLAlchemy model definitions corresponding to
database tables for entities like customers, products, categories, etc.
"""
from .customer import Customer
from .category import Category
from .product import Product
from .shopping_cart import ShoppingCart
from .cart_item import CartItem
