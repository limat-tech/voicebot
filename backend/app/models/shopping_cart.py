from app import db
from datetime import datetime

class ShoppingCart(db.Model):
    __tablename__ = 'shoppingcarts' # Matches the SQL table name from the plan

    cart_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False, unique=True) # Assuming one active cart per customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to customer (could also be defined in Customer model via backref)
    # customer = db.relationship('Customer', backref=db.backref('shopping_cart', uselist=False)) # uselist=False for one-to-one

    # Relationship to cart items
    items = db.relationship('CartItem', backref='shopping_cart', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ShoppingCart {self.cart_id} for Customer {self.customer_id}>'

    # Potential methods:
    # def get_total_price(self):
    #     return sum(item.get_subtotal() for item in self.items)
