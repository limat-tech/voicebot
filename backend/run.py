from app import create_app, db # Import db for migration context
from app.models import Customer, Category, Product, ShoppingCart, CartItem # Import all models
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# This makes 'db' and your models available to Flask-Migrate commands
# when FLASK_APP is set to run.py
@app.shell_context_processor
def make_shell_context():
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
