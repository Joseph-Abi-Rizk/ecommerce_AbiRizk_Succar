from flask import Flask
from database.models import db, Customer, Inventory, Sale, Review  # Import the models
from customers.app import app  # Import app to use the same context

# Initialize the app with the same config as in the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Re-initialize the database with the app context
with app.app_context():
    # Drop all existing tables (use cautiously, it will delete all data)
    db.drop_all()
    
    # Create the new tables based on the models
    db.create_all()

    print("Database reinitialized successfully.")