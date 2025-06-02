from flask import Blueprint, request, jsonify
from app.models.product import Product # Import your Product model
# from app.models.category import Category # Not directly used in these specific endpoints but good to remember
from app import db # Import the SQLAlchemy db instance
from sqlalchemy import or_ # For more complex OR queries in search

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET']) # Route is /api/products
def get_products():
    try:
        # Query for all products that are active
        products_query = Product.query.filter_by(is_active=True).all()
        
        result = []
        for product in products_query:
            result.append({
                "product_id": product.product_id,
                "name_en": product.name_en,
                "name_ar": product.name_ar,
                "description_en": product.description_en,
                "description_ar": product.description_ar,
                "price": float(product.price) if product.price is not None else None, # Ensure price is float
                "category_id": product.category_id,
                "brand": product.brand,
                "stock_quantity": product.stock_quantity,
                "unit_type": product.unit_type,
                "image_url": product.image_url
                # "created_at": product.created_at.isoformat() # Optional: if you want to include it
            })
        return jsonify({"products": result}), 200
    except Exception as e:
        # Log the exception e here for debugging
        return jsonify({"error": "An error occurred while fetching products."}), 500

@products_bp.route('/search', methods=['GET']) # Route is /api/products/search
def search_products():
    query_param = request.args.get('q', '') # Get search query, default to empty string
    language = request.args.get('language', 'en') # Default to English

    if not query_param:
        return jsonify({"error": "Search query parameter 'q' is required."}), 400

    try:
        # Build the search filter
        search_filter = Product.is_active == True # Always filter for active products
        
        if language.lower() == 'ar':
            # Search in Arabic name and description
            search_filter = db.and_(search_filter, or_(
                Product.name_ar.ilike(f"%{query_param}%"),
                Product.description_ar.ilike(f"%{query_param}%")
            ))
        else: # Default to English
            # Search in English name and description
            search_filter = db.and_(search_filter, or_(
                Product.name_en.ilike(f"%{query_param}%"),
                Product.description_en.ilike(f"%{query_param}%")
            ))

        products_query = Product.query.filter(search_filter).all()

        result = []
        for product in products_query:
            result.append({
                "product_id": product.product_id,
                "name_en": product.name_en,
                "name_ar": product.name_ar,
                "description_en": product.description_en,
                "description_ar": product.description_ar,
                "price": float(product.price) if product.price is not None else None,
                "category_id": product.category_id,
                "brand": product.brand,
                "stock_quantity": product.stock_quantity,
                "unit_type": product.unit_type,
                "image_url": product.image_url
            })
        return jsonify({"products": result}), 200
    except Exception as e:
        # Log the exception e here
        return jsonify({"error": "An error occurred during product search."}), 500
