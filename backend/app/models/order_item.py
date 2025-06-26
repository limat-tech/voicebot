from app import db
from decimal import Decimal # For price_at_purchase

class OrderItem(db.Model):
    __tablename__ = 'orderitems'

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False) # Or nullable if product can be deleted
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False) # Price of one unit of the product when the order was placed

    # Optional: Relationship to Product (Many order items can refer to one product)
    # product = db.relationship('Product') 

    def __repr__(self):
        return f'<OrderItem {self.order_item_id} Product {self.product_id} Qty {self.quantity} Price {self.price_at_purchase}>'

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
