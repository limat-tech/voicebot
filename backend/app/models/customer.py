from app import db # Corrected: db should be imported from the app package where it's initialized
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Storing hash, not raw password
    phone_number = db.Column(db.String(15), nullable=True)
    preferred_language = db.Column(db.String(2), default='en') # e.g., 'en', 'ar'
    store_credit_balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Optional

    # Relationships can be added later, e.g., to shopping carts, orders
    # shopping_carts = db.relationship('ShoppingCart', backref='customer', lazy=True)
    # orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name} ({self.email})>'

    # Methods for setting/checking password can be added here later
    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
