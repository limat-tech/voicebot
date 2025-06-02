from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from app.models.customer import Customer # Import your Customer model
from app import db # Import the SQLAlchemy db instance

# Create a Blueprint for authentication routes
# 'auth' is the name of the blueprint
# __name__ helps Flask locate the blueprint
# url_prefix='/api/auth' means all routes in this blueprint will start with /api/auth
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    # Get data from the JSON request body
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    preferred_language = data.get('preferred_language', 'en') # Default to 'en' if not provided

    # Basic validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not name: # As per your plan's example, name seems to be required too
        return jsonify({"error": "Name, email and password are required"}), 400

    # Check if user (customer) already exists
    if Customer.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400 # 400 or 409 Conflict

    # Create new user (customer)
    # Hash the password before storing it
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256') # Updated method

    new_customer = Customer(
        name=name,
        email=email,
        password_hash=hashed_password,
        phone_number=phone_number,
        preferred_language=preferred_language
    )

    # Add to database session and commit
    try:
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "User created successfully", "customer_id": new_customer.customer_id}), 201 # 201 Created
    except Exception as e:
        db.session.rollback()
        # Log the exception e here for debugging
        return jsonify({"error": "An error occurred while creating the user."}), 500
