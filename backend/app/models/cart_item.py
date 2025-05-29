from app import db

class CartItem(db.Model):
    __tablename__ = 'cartitems' # Matches the SQL table name from the plan

    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('shoppingcarts.cart_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # price_at_addition = db.Column(db.Numeric(10, 2), nullable=False) # Optional: store price when added

    # Relationships to product and shopping cart are established via backrefs from those models
    # but you can define them explicitly here if preferred.
    product = db.relationship('Product') # Eager load product details with cart item

    def __repr__(self):
        return f'<CartItem {self.cart_item_id} (Product {self.product_id}, Qty {self.quantity})>'

    # def get_subtotal(self):
    #     return self.product.price * self.quantity
