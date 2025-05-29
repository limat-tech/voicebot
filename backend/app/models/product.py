from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products' # Matches the SQL table name from the plan

    product_id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(255), nullable=False)
    name_ar = db.Column(db.String(255), nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    description_ar = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False) # Using Numeric for precision with currency
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)
    unit_type = db.Column(db.String(20), nullable=True) # e.g., 'kg', 'piece', 'liter'
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Optional

    # Relationship to cart items can be added later if needed from Product side
    # cart_items = db.relationship('CartItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name_en}>'
