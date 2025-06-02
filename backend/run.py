"""
Entry point script for running the Flask development server.

This script creates the Flask application instance using the factory
and runs the development server. It also provides a shell context
for `flask shell` with database and model access.
"""
from app import create_app, db # Import db for migration context
from app.models import Customer, Category, Product, ShoppingCart, CartItem # Import all models
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# This makes 'db' and your models available to Flask-Migrate commands
# when FLASK_APP is set to run.py
@app.shell_context_processor
def make_shell_context():
    """
    Provide a shell context for `flask shell`.

    Makes the database instance and models available in the shell
    without explicit imports.
    """
    return {
        'db': db, 
        'Customer': Customer, 
        'Category': Category,
        'Product': Product, 
        'ShoppingCart': ShoppingCart, 
        'CartItem': CartItem
    }

if __name__ == '__main__':
    app.run(debug=True) # debug=True is good for development
