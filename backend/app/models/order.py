from app import db
from datetime import datetime
from decimal import Decimal # For total_amount

class Order(db.Model):
    __tablename__ = 'orders' # As per your long-term plan's schema list

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False) # Example: stores up to 9,999,999.99
    status = db.Column(db.String(50), nullable=False, default='pending') # e.g., 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    
    # Optional: Shipping address details can be stored here or in a separate linked table
    # shipping_address_line1 = db.Column(db.String(255))
    # shipping_city = db.Column(db.String(100))
    # shipping_postal_code = db.Column(db.String(20))
    # shipping_country = db.Column(db.String(50))

    # Relationship to Customer (Many orders can belong to one customer)
    # customer = db.relationship('Customer', backref='orders')

    # Relationship to OrderItems (One order has many order items)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.order_id} Status {self.status} Total {self.total_amount}>'
