"""
Product-related routes for the Flask application.

Handles listing, searching, and retrieving details for products
with full bilingual support - returns both English and Arabic names.
"""
from flask import Blueprint, request, jsonify
from app.models.product import Product
from app import db
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def get_products():
    """
    Retrieve a list of all active products with both English and Arabic names.
    Returns both language versions so frontend can display title/subtitle.
    """
    logger.info("Fetching all active products with bilingual support")
    try:
        products = Product.query.filter_by(is_active=True).all()
        result = []
        for product in products:
            result.append({
                'product_id': product.product_id,
                'name_en': product.name_en,
                'name_ar': product.name_ar,
                'description_en': product.description_en,
                'description_ar': product.description_ar,
                'price': float(product.price),
                'brand': product.brand,
                'stock_quantity': product.stock_quantity,
                'unit_type': product.unit_type,
                'image_url': product.image_url,
                'category_id': product.category_id,
                'is_active': product.is_active
            })
        
        logger.info(f"Successfully fetched {len(result)} products with bilingual data.")
        return jsonify({"products": result}), 200
    except Exception as e:
        logger.error("Error fetching products.", exc_info=True)
        return jsonify({"error": "An error occurred while fetching products."}), 500

@products_bp.route('/search', methods=['GET'])
def search_products():
    """
    Search for active products in both English and Arabic.
    Returns bilingual results regardless of search language.
    ?q=search_term&lang=en/ar (lang used to determine which fields to search in)
    """
    query_param = request.args.get('q', '')
    lang = request.args.get('lang', 'en').lower()

    if not query_param:
        return jsonify({"error": "Search query parameter 'q' is required."}), 400

    logger.info(f"Searching for '{query_param}' in language context: {lang}")
    try:
        search_filter = Product.is_active == True
        
        if lang == 'ar':
            # Search in Arabic fields but return bilingual results
            search_filter = db.and_(search_filter, or_(
                Product.name_ar.ilike(f"%{query_param}%"),
                Product.description_ar.ilike(f"%{query_param}%")
            ))
        else:
            # Search in English fields but return bilingual results
            search_filter = db.and_(search_filter, or_(
                Product.name_en.ilike(f"%{query_param}%"),
                Product.description_en.ilike(f"%{query_param}%")
            ))

        products = Product.query.filter(search_filter).all()
        result = []
        for product in products:
            result.append({
                'product_id': product.product_id,
                'name_en': product.name_en,
                'name_ar': product.name_ar,
                'description_en': product.description_en,
                'description_ar': product.description_ar,
                'price': float(product.price),
                'brand': product.brand,
                'stock_quantity': product.stock_quantity,
                'unit_type': product.unit_type,
                'image_url': product.image_url,
                'category_id': product.category_id,
                'is_active': product.is_active
            })
        
        logger.info(f"Found {len(result)} products matching search criteria.")
        return jsonify({"products": result}), 200
    except Exception as e:
        logger.error(f"Error during product search for query '{query_param}'.", exc_info=True)
        return jsonify({"error": "An error occurred during product search."}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Returns details for a single product with both English and Arabic names.
    """
    logger.info(f"Fetching product ID {product_id} with bilingual data")
    
    product = db.session.get(Product, product_id)
    
    if not product or not product.is_active:
        return jsonify({"error": "Product not found or is not active"}), 404
    
    result = {
        'product_id': product.product_id,
        'name_en': product.name_en,
        'name_ar': product.name_ar,
        'description_en': product.description_en,
        'description_ar': product.description_ar,
        'price': float(product.price),
        'brand': product.brand,
        'stock_quantity': product.stock_quantity,
        'unit_type': product.unit_type,
        'image_url': product.image_url,
        'category_id': product.category_id,
        'is_active': product.is_active
    }
    
    return jsonify(result), 200