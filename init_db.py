from flask import Flask
from database.models import db, Customer, Inventory, Sale, Review  # Import the models
from customers.app import app  # Import app to use the same context

# Initialize the app with the same config as in the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Re-initialize the database with the app context
with app.app_context():
    """
    Reinitializes the database.

    This script uses the Flask app context to:
        1. Drop all existing tables in the database.
        2. Recreate the database tables as defined in the models.
    
    Models used:
        - Customer
        - Inventory
        - Sale
        - Review
    
    **Caution**:
        The `db.drop_all()` command will delete all existing data.
        Use this script only when resetting the database is required.

    Prints:
        A confirmation message ("Database reinitialized successfully.") upon completion.
    """
    # Drop all existing tables (use cautiously, it will delete all data)
    db.drop_all()
    
    # Create the new tables based on the models
    db.create_all()

    print("Database reinitialized successfully.")