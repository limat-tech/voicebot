from app import db
from datetime import datetime

class Product(db.Model):
    """
    Represents a product available for sale.

    Attributes:
        product_id (int): Primary key for the product.
        name_en (str): Name of the product in English.
        name_ar (str, optional): Name of the product in Arabic.
        description_en (str, optional): Description in English.
        description_ar (str, optional): Description in Arabic.
        price (Decimal): Price of the product.
        category_id (int): Foreign key linking to the Category model.
        brand (str, optional): Brand of the product.
        stock_quantity (int): Current stock quantity.
        unit_type (str, optional): Unit of measurement (e.g., 'kg', 'piece').
        image_url (str, optional): URL for the product image.
        is_active (bool): Whether the product is currently active for sale.
        created_at (datetime): Timestamp of when the product was added.
    """
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
