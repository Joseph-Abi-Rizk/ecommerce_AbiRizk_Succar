from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Add goods
@app.route('/inventory/add', methods=['POST'])
def add_goods():
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
    items = Inventory.query.all()
    inventory_list = [
        {"id": item.id, "name": item.name, "category": item.category, "price": item.price, "count": item.count}
        for item in items
    ]
    return jsonify(inventory_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
