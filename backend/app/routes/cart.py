# app/routes/cart.py
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.shopping_cart import ShoppingCart # Your ShoppingCart model
from app.models.cart_item import CartItem       # Your CartItem model
from app.models.product import Product
from decimal import Decimal

# from app.models.customer import Customer # Not directly queried if using JWT identity
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user identity in token. Must be an integer."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Request body must be JSON."}), 400

    product_id_input = data.get('product_id')
    quantity_input = data.get('quantity', 1)

    if not product_id_input:
        return jsonify({"msg": "Product ID is required."}), 400
    try:
        product_id = int(product_id_input)
    except ValueError:
        return jsonify({"msg": "Product ID must be an integer."}), 400
    
    try:
        quantity = int(quantity_input)
    except ValueError:
        return jsonify({"msg": "Quantity must be an integer."}), 400
    
    if quantity <= 0:
        return jsonify({"msg": "Quantity must be a positive integer."}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": f"Product with ID {product_id} not found."}), 404
    if not product.is_active:
        return jsonify({"msg": f"Product '{product.name_en}' is currently unavailable."}), 400
    
    shopping_cart = ShoppingCart.query.filter_by(customer_id=current_user_id).first()
    if not shopping_cart:
        shopping_cart = ShoppingCart(customer_id=current_user_id)
        db.session.add(shopping_cart)
        db.session.flush() 

    cart_item = CartItem.query.filter_by(cart_id=shopping_cart.cart_id, product_id=product_id).first()

    if cart_item:
        new_quantity_in_cart = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity_in_cart:
            return jsonify({"msg": f"Insufficient stock for '{product.name_en}'. Requested total: {new_quantity_in_cart}, Available: {product.stock_quantity}"}), 400
        cart_item.quantity = new_quantity_in_cart
    else:
        if product.stock_quantity < quantity:
            return jsonify({"msg": f"Insufficient stock for '{product.name_en}'. Requested: {quantity}, Available: {product.stock_quantity}"}), 400
        cart_item = CartItem(cart_id=shopping_cart.cart_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding to cart for customer {current_user_id}, product {product_id}: {str(e)}")
        return jsonify({"msg": "An error occurred while adding the item to the cart.", "error_details": str(e)}), 500
            
    return jsonify({
        "msg": f"'{product.name_en}' (Qty: {quantity} requested) processed for cart.",
        "cart_item_details": {
            # using cart_item_id from your model
            "cart_item_id": cart_item.cart_item_id, 
            "product_id": cart_item.product_id,
            "product_name": product.name_en,
            "updated_quantity_in_cart": cart_item.quantity,
            "cart_id": shopping_cart.cart_id
        }
    }), 200

@cart_bp.route('', methods=['GET'])
@jwt_required()
def view_cart():
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user identity in token. Must be an integer."}), 400

    shopping_cart = ShoppingCart.query.filter_by(customer_id=current_user_id).first()

    if not shopping_cart:
        return jsonify({"msg": "Your shopping cart is empty.", "items": [], "total_price": 0.0}), 200

    cart_items_query_result = shopping_cart.items.all()

    if not cart_items_query_result:
        return jsonify({
            "cart_id": shopping_cart.cart_id,
            "msg": "Your shopping cart is empty.",
            "items": [],
            "total_price": 0.0
        }), 200

    items_response = []
    # Initialize grand_total_price as a Decimal
    grand_total_price = Decimal('0.0')

    for item in cart_items_query_result:
        product = Product.query.get(item.product_id)
        
        if product:
            # product.price is Decimal, item.quantity is int.
            # item_subtotal will be Decimal.
            item_subtotal = product.price * item.quantity
            
            items_response.append({
                "cart_item_id": item.cart_item_id,
                "product_id": product.product_id,
                "name_en": product.name_en,
                "name_ar": product.name_ar,
                "price_per_unit": float(product.price), # Still convert to float for individual item display
                "quantity": item.quantity,
                "unit_type": product.unit_type,
                "image_url": product.image_url,
                "subtotal": float(item_subtotal) # Still convert to float for individual item display
            })
            # Now this is Decimal += Decimal, which is valid
            grand_total_price += item_subtotal
        else:
            current_app.logger.warning(f"Data integrity issue: Product ID {item.product_id} found in cart (cart_item_id: {item.cart_item_id}, cart_id: {shopping_cart.cart_id}) but no matching product in products table.")
            
    return jsonify({
        "cart_id": shopping_cart.cart_id,
        "customer_id": shopping_cart.customer_id,
        "items": items_response,
        # Convert the final Decimal grand_total_price to float for JSON serialization
        "total_price": float(grand_total_price)
    }), 200

@cart_bp.route('/items/<int:cart_item_id_from_url>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(cart_item_id_from_url):
    """
    Removes a specific item from the authenticated user's shopping cart.
    Path parameter: cart_item_id_from_url (the ID of the cart item to remove)
    """
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user identity in token."}), 400

    # Find the cart item to be deleted
    cart_item_to_delete = CartItem.query.get(cart_item_id_from_url)

    if not cart_item_to_delete:
        return jsonify({"msg": "Cart item not found."}), 404

    # Security Check: Verify the item belongs to the current user's cart
    # 1. Get the user's shopping cart
    user_shopping_cart = ShoppingCart.query.filter_by(customer_id=current_user_id).first()
    if not user_shopping_cart:
        # This user doesn't even have a cart, so the item can't be theirs.
        return jsonify({"msg": "Shopping cart not found for user."}), 404 
    
    # 2. Check if the cart_item's cart_id matches the user's shopping_cart.cart_id
    if cart_item_to_delete.cart_id != user_shopping_cart.cart_id:
        # The item exists, but it's not in this user's cart!
        current_app.logger.warning(
            f"Security attempt: User {current_user_id} tried to delete cart_item {cart_item_id_from_url} "
            f"which belongs to cart {cart_item_to_delete.cart_id}, not their cart {user_shopping_cart.cart_id}."
        )
        return jsonify({"msg": "This item does not belong to your cart."}), 403 # Forbidden

    # If all checks pass, delete the item
    try:
        db.session.delete(cart_item_to_delete)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing cart item {cart_item_id_from_url}: {str(e)}")
        return jsonify({"msg": "Error removing item from cart.", "error_details": str(e)}), 500
    
    return jsonify({"msg": f"Cart item with ID {cart_item_id_from_url} removed successfully."}), 200

@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user_id_str = get_jwt_identity()
    result = process_checkout(customer_id=current_user_id_str)

    if not result['success']:
        return jsonify({"msg": "Checkout process failed.", "error_details": result['error']}), result['status_code']

    return jsonify({
        "msg": "Order placed successfully!",
        "order_id": result['order_id'],
        "total_amount": float(result['total_amount'])
    }), result['status_code']

@cart_bp.route('/items/<int:cart_item_id_from_url>', methods=['PUT'])
@jwt_required()
def update_cart_item_quantity(cart_item_id_from_url):
    """
    Updates the quantity of a specific item in the authenticated user's shopping cart.
    If the new quantity is 0, the item is removed.
    Path parameter: cart_item_id_from_url (the ID of the cart item to update)
    Expects JSON: {"quantity": <new_quantity_int>}
    """
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user identity in token."}), 400

    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({"msg": "New quantity is required in JSON body."}), 400

    try:
        new_quantity = int(data['quantity'])
    except ValueError:
        return jsonify({"msg": "Quantity must be an integer."}), 400

    if new_quantity < 0:
        return jsonify({"msg": "Quantity cannot be negative."}), 400

    # Find the cart item to be updated
    cart_item_to_update = CartItem.query.get(cart_item_id_from_url)

    if not cart_item_to_update:
        return jsonify({"msg": "Cart item not found."}), 404

    # Security Check: Verify the item belongs to the current user's cart
    user_shopping_cart = ShoppingCart.query.filter_by(customer_id=current_user_id).first()
    if not user_shopping_cart or cart_item_to_update.cart_id != user_shopping_cart.cart_id:
        current_app.logger.warning(
            f"Security attempt: User {current_user_id} tried to update cart_item {cart_item_id_from_url} "
            f"not belonging to their cart."
        )
        return jsonify({"msg": "This item does not belong to your cart."}), 403

    # Handle quantity update
    if new_quantity == 0:
        # If new quantity is 0, remove the item
        try:
            db.session.delete(cart_item_to_update)
            db.session.commit()
            return jsonify({"msg": f"Cart item with ID {cart_item_id_from_url} removed as quantity set to 0."}), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error removing cart item {cart_item_id_from_url} (quantity 0): {str(e)}")
            return jsonify({"msg": "Error processing cart item removal.", "error_details": str(e)}), 500
    else:
        # If new quantity > 0, update the quantity
        product = Product.query.get(cart_item_to_update.product_id)
        if not product:
            # Should not happen if data integrity is maintained
            return jsonify({"msg": "Associated product not found. Cannot update quantity."}), 404 
        
        if not product.is_active:
             return jsonify({"msg": f"Product '{product.name_en}' is currently unavailable."}), 400

        if product.stock_quantity < new_quantity:
            return jsonify({"msg": f"Insufficient stock for '{product.name_en}'. Requested: {new_quantity}, Available: {product.stock_quantity}"}), 400
        
        cart_item_to_update.quantity = new_quantity
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating cart item {cart_item_id_from_url} quantity: {str(e)}")
            return jsonify({"msg": "Error updating item quantity.", "error_details": str(e)}), 500

        return jsonify({
            "msg": f"Quantity for cart item ID {cart_item_id_from_url} updated to {new_quantity}.",
            "cart_item_details": {
                "cart_item_id": cart_item_to_update.cart_item_id, # Using your model's PK name
                "product_id": cart_item_to_update.product_id,
                "product_name": product.name_en,
                "new_quantity": cart_item_to_update.quantity,
                "cart_id": cart_item_to_update.cart_id
            }
        }), 200
    
@cart_bp.route('/items/<int:item_id>', methods=['PATCH'])
@jwt_required()
def update_cart_item(item_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_quantity = data.get('quantity')

    if not new_quantity or not isinstance(new_quantity, int) or new_quantity <= 0:
        return jsonify({"error": "A valid quantity is required"}), 400

    cart_item = CartItem.query.get_or_404(item_id)

    # Security check: Ensure the item belongs to the current user's cart
    cart = ShoppingCart.query.filter_by(customer_id=current_user_id, cart_id=cart_item.cart_id).first()
    if not cart:
        return jsonify({"error": "Item not found in your cart"}), 404

    # Check stock
    product = Product.query.get(cart_item.product_id)
    if product.stock_quantity < new_quantity:
        return jsonify({"error": f"Insufficient stock for {product.name_en}. Only {product.stock_quantity} available."}), 400

    cart_item.quantity = new_quantity
    db.session.commit()

    return jsonify({"message": "Cart updated successfully"}), 200