from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Add goods
@app.route('/inventory/add', methods=['POST'])
def add_goods():
    """
    Adds a new item to the inventory.

    This function handles the creation of a new inventory item by accepting data in JSON format.
    It then adds the new item to the database and returns a success message.

    Arguments:
        None (data is expected in the request body)

    Returns:
        JSON response with a success message.
        - Success: {"message": "Item added successfully"}, status code 201
    """
    data = request.get_json()
    new_item = Inventory(
        name=data['name'],
        category=data['category'],
        price=data['price'],
        description=data.get('description', ''),
        count=data['count']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item added successfully"}), 201

# Update goods
@app.route('/inventory/update/<int:item_id>', methods=['PUT'])
def update_goods(item_id):
    """
    Updates an existing inventory item.

    This function handles the update of an inventory item's details (such as name, category, price, etc.) 
    based on the provided `item_id` and the data in the request body.

    Arguments:
        item_id (int): The ID of the inventory item to be updated.
    
    Request Data:
        JSON data containing fields to update (e.g., name, category, price, etc.)

    Returns:
        JSON response with a success message or error message.
        - Success: {"message": "Item updated successfully"}, status code 200
        - Failure: {"message": "Item not found"}, status code 404
    """
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    data = request.get_json()
    if 'name' in data: item.name = data['name']
    if 'category' in data: item.category = data['category']
    if 'price' in data: item.price = data['price']
    if 'description' in data: item.description = data['description']
    if 'count' in data: item.count = data['count']
    db.session.commit()
    return jsonify({"message": "Item updated successfully"})

# Deduct goods
@app.route('/inventory/deduct/<int:item_id>', methods=['POST'])
def deduct_goods(item_id):
    """
    Deducts a specified quantity of an inventory item.

    This function reduces the stock count of an inventory item by the specified quantity.
    If the stock is insufficient, it returns an error message.

    Arguments:
        item_id (int): The ID of the inventory item for which the stock is to be deducted.
    
    Request Data:
        JSON data containing the `count` to deduct from the stock.

    Returns:
        JSON response with success message, remaining stock, or error message.
        - Success: {"message": "Stock deducted successfully", "remaining_count": <remaining_count>}, status code 200
        - Failure: {"message": "Item not found"} or {"message": "Insufficient stock"}, status code 404 or 400
    """

    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    data = request.get_json()
    if item.count < data['count']:
        return jsonify({"message": "Insufficient stock"}), 400
    item.count -= data['count']
    db.session.commit()
    return jsonify({"message": "Stock deducted successfully", "remaining_count": item.count})

# Get all inventory items
@app.route('/inventory', methods=['GET'])
def get_inventory():
    """
    Retrieves all items from the inventory.

    This function fetches all inventory items from the database and returns them in a list of JSON objects 
    containing basic information such as item ID, name, category, price, and stock count.

    Arguments:
        None

    Returns:
        JSON response with a list of inventory items.
        - Success: A list of items with details (id, name, category, price, count), status code 200
    """
    items = Inventory.query.all()
    inventory_list = [
        {"id": item.id, "name": item.name, "category": item.category, "price": item.price, "count": item.count}
        for item in items
    ]
    return jsonify(inventory_list)

if __name__ == '__main__':
    """
    Runs the Flask application.

    Starts the Flask web server on host 0.0.0.0 and port 5002 in debug mode.

    Arguments:
        None

    Returns:
        None
    """
    app.run(debug=True, host='0.0.0.0', port=5002)
