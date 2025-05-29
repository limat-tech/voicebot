from app import db # Imports the SQLAlchemy instance from app/__init__.py
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories' # Matches the SQL table name from the plan

    category_id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=True) # Assuming Arabic name can be optional initially
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True) # Self-referential for subcategories

    # Relationship to products
    products = db.relationship('Product', backref='category', lazy=True)
    # Relationship for subcategories (if you want to navigate parent-child easily)
    # parent = db.relationship('Category', remote_side=[category_id], backref='subcategories')


    def __repr__(self):
        return f'<Category {self.name_en}>'
