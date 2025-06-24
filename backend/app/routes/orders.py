# VOCERY/backend/app/routes/orders.py
from flask import Blueprint, jsonify
from app import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """
    Retrieve all orders for the authenticated user.
    Returns a list of orders with basic information.
    """
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(customer_id=current_user_id).order_by(Order.order_date.desc()).all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'order_id': order.order_id,
            'order_date': order.order_date.isoformat(),
            'total_amount': float(order.total_amount),
            'status': order.status
        })
    
    return jsonify(orders_data), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """
    Retrieve detailed information for a specific order including bilingual product names.
    Returns order details with both English and Arabic product names for each item.
    """
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(order_id=order_id, customer_id=current_user_id).first_or_404()

    items_data = []
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            # Include both English and Arabic product names
            item_info = {
                'product_name': product.name_en,        # English name (primary)
                'product_name_ar': product.name_ar,     # Arabic name (secondary)
                'quantity': item.quantity,
                'price_at_purchase': float(item.price_at_purchase)
            }
        else:
            # Fallback for deleted/missing products
            item_info = {
                'product_name': "Unknown Product",
                'product_name_ar': "منتج غير معروف",     # Arabic fallback
                'quantity': item.quantity,
                'price_at_purchase': float(item.price_at_purchase)
            }
        
        items_data.append(item_info)

    order_details = {
        'order_id': order.order_id,
        'order_date': order.order_date.isoformat(),
        'total_amount': float(order.total_amount),
        'status': order.status,
        'items': items_data
    }
    
    return jsonify(order_details), 200
