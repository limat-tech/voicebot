"""
Script to seed the database with initial sample data.

This script should be run manually to populate categories and products
for development and testing purposes. It requires an active Flask app context.
"""
from app import create_app, db # To access app context and db instance
from app.models.category import Category # Import your Category model
from app.models.product import Product   # Import your Product model
# Import other models if you need to seed them, e.g., Customer

# Create a Flask app instance to work within its context
# This is necessary for SQLAlchemy to know which database to connect to
# and to use the application's configuration.
app = create_app()

def seed_database():
    # app.app_context() provides the application context.
    # Operations that interact with the Flask app (like database operations
    # using Flask-SQLAlchemy) need to run within an active app context.
    with app.app_context():
        # --- Clean up existing data (optional, but useful for re-running seed) ---
        # This will delete all products and then all categories.
        # Be careful with this in a production environment!
        # For development, it helps ensure a clean slate each time you seed.
        print("Deleting existing products...")
        Product.query.delete()
        print("Deleting existing categories...")
        Category.query.delete()
        db.session.commit() # Commit deletions
        print("Existing data cleared.")

        # --- Add Categories ---
        print("Adding categories...")
        fruits = Category(name_en="Fruits", name_ar="فواكه")
        vegetables = Category(name_en="Vegetables", name_ar="خضروات")
        dairy = Category(name_en="Dairy", name_ar="منتجات الألبان")
        
        db.session.add_all([fruits, vegetables, dairy])
        db.session.commit() # Commit categories so their IDs are generated
        print(f"Added categories: Fruits (ID: {fruits.category_id}), Vegetables (ID: {vegetables.category_id}), Dairy (ID: {dairy.category_id})")

        # --- Add Products ---
        print("Adding products...")
        # Ensure you use the .category_id obtained after committing categories
        apple = Product(
            name_en="Red Apple", name_ar="تفاح أحمر",
            description_en="Fresh and juicy red apples.", description_ar="تفاح أحمر طازج وعصيري.",
            price=5.99, category_id=fruits.category_id, stock_quantity=100, unit_type="kg",
            brand="FarmFresh", image_url="https://example.com/images/red_apple.jpg", is_active=True
        )
        banana = Product(
            name_en="Banana", name_ar="موز",
            description_en="Ripe yellow bananas.", description_ar="موز أصفر ناضج.",
            price=3.49, category_id=fruits.category_id, stock_quantity=150, unit_type="dozen",
            brand="TropicalSun", image_url="https://example.com/images/banana.jpg", is_active=True
        )
        milk = Product(
            name_en="Fresh Milk", name_ar="حليب طازج",
            description_en="Full cream dairy milk, 1 liter.", description_ar="حليب بقري كامل الدسم، 1 لتر.",
            price=2.99, category_id=dairy.category_id, stock_quantity=80, unit_type="liter",
            brand="DailyDairy", image_url="https://example.com/images/milk.jpg", is_active=True
        )
        carrot = Product(
            name_en="Carrot", name_ar="جزر",
            description_en="Organic carrots, 1kg pack.", description_ar="جزر عضوي، عبوة 1 كجم.",
            price=4.20, category_id=vegetables.category_id, stock_quantity=120, unit_type="kg",
            brand="GreenValley", image_url="https://example.com/images/carrot.jpg", is_active=True
        )

        db.session.add_all([apple, banana, milk, carrot])
        db.session.commit()
        print("Added products.")
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    # This allows you to run the script directly using "python seed_data.py"
    seed_database()
