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
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(order_id=order_id, customer_id=current_user_id).first_or_404()

    items_data = []
    for item in order.items:
        product = Product.query.get(item.product_id)
        items_data.append({
            'product_name': product.name_en if product else "Unknown Product",
            'quantity': item.quantity,
            'price_at_purchase': float(item.price_at_purchase)
        })

    order_details = {
        'order_id': order.order_id,
        'order_date': order.order_date.isoformat(),
        'total_amount': float(order.total_amount),
        'status': order.status,
        'items': items_data
    }
    
    return jsonify(order_details), 200
