"""
Product-related routes for the Flask application.

Handles listing, searching, and retrieving details for products
with full bilingual support.
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
    Retrieve a list of all active products, translated based on the 'lang' parameter.
    ?lang=ar or ?lang=en
    """
    lang = request.args.get('lang', 'en').lower()
    logger.info(f"Fetching all active products for language: {lang}")
    try:
        products = Product.query.filter_by(is_active=True).all()
        # Use a list comprehension and our new to_dict method. Clean and efficient!
        result = [p.to_dict(lang=lang) for p in products]
        logger.info(f"Successfully fetched {len(result)} products.")
        return jsonify({"products": result}), 200
    except Exception as e:
        logger.error("Error fetching products.", exc_info=True)
        return jsonify({"error": "An error occurred while fetching products."}), 500

@products_bp.route('/search', methods=['GET'])
def search_products():
    """
    Search for active products based on a query string in either English or Arabic.
    ?q=...&lang=...
    """
    query_param = request.args.get('q', '')
    lang = request.args.get('lang', 'en').lower() # Use 'lang' for consistency

    if not query_param:
        return jsonify({"error": "Search query parameter 'q' is required."}), 400

    logger.info(f"Searching for '{query_param}' in language: {lang}")
    try:
        search_filter = Product.is_active == True
        
        if lang == 'ar':
            search_filter = db.and_(search_filter, or_(
                Product.name_ar.ilike(f"%{query_param}%"),
                Product.description_ar.ilike(f"%{query_param}%")
            ))
        else: # Default to English
            search_filter = db.and_(search_filter, or_(
                Product.name_en.ilike(f"%{query_param}%"),
                Product.description_en.ilike(f"%{query_param}%")
            ))

        products_query = Product.query.filter(search_filter).all()
        # Again, just call to_dict. No more manual dictionary building.
        result = [p.to_dict(lang=lang) for p in products_query]
        return jsonify({"products": result}), 200
    except Exception as e:
        logger.error(f"Error during product search for query '{query_param}'.", exc_info=True)
        return jsonify({"error": "An error occurred during product search."}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Returns details for a single product, translated based on the 'lang' parameter.
    """
    lang = request.args.get('lang', 'en').lower()
    logger.info(f"Fetching product ID {product_id} for language: {lang}")
    
    # Using db.session.get is the modern, recommended way to fetch by primary key.
    product = db.session.get(Product, product_id)
    
    if not product or not product.is_active:
        return jsonify({"error": "Product not found or is not active"}), 404
    
    # Simply call to_dict to get the language-specific response.
    return jsonify(product.to_dict(lang=lang)), 200