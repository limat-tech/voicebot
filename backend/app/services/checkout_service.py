# In backend/app/services/checkout_service.py

from flask import current_app # <-- Import current_app directly from Flask
from app import db            # Keep importing db from your app package
from app.models.shopping_cart import ShoppingCart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from decimal import Decimal

def process_checkout(customer_id: int):
    """
    Processes the checkout for a given customer.
    Creates an order, decrements stock, and clears the cart.
    Returns a dictionary with the result.
    """
    shopping_cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()

    if not shopping_cart or not shopping_cart.items.first():
        return {"success": False, "error": "Your shopping cart is empty.", "status_code": 400}

    order_items_data = []
    calculated_total = Decimal('0.0')
    cart_items_to_process = shopping_cart.items.all()

    try:
        # Validate stock and prepare order data
        for item in cart_items_to_process:
            # Lock the product row for the duration of the transaction to prevent race conditions
            product = Product.query.with_for_update().get(item.product_id)
            if not product or not product.is_active or product.stock_quantity < item.quantity:
                raise ValueError(f"Insufficient stock or unavailable product: {product.name_en if product else 'N/A'}")
            
            price = product.price
            order_items_data.append({
                'product': product,
                'quantity': item.quantity,
                'price_at_purchase': price
            })
            calculated_total += price * item.quantity

        # Create the Order
        new_order = Order(customer_id=customer_id, total_amount=calculated_total, status='pending')
        db.session.add(new_order)
        db.session.flush()  # Get the new_order.order_id

        # Create OrderItems and decrement stock
        for data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=data['product'].product_id,
                quantity=data['quantity'],
                price_at_purchase=data['price_at_purchase']
            )
            db.session.add(order_item)
            data['product'].stock_quantity -= data['quantity']

        # Clear the cart
        for item in cart_items_to_process:
            db.session.delete(item)

        db.session.commit() # Commit the entire transaction

        return {
            "success": True,
            "order_id": new_order.order_id,
            "total_amount": new_order.total_amount,
            "status_code": 201
        }

    except Exception as e:
        db.session.rollback() # Roll back all changes if any part of the transaction fails
        # Now this logger call will work correctly
        current_app.logger.error(f"Checkout service failed for user {customer_id}: {str(e)}")
        return {"success": False, "error": str(e), "status_code": 400}
