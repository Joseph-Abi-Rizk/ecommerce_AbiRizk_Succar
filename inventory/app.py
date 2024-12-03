import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database.models import db, Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Performance profiling: Start profiling before each request
@app.before_request
def start_profiling():
    request.profiler = cProfile.Profile()
    request.profiler.enable()

# Performance profiling: Stop profiling and log results after each request
@app.after_request
def stop_profiling(response):
    if hasattr(request, 'profiler'):
        request.profiler.disable()
        s = StringIO()
        ps = pstats.Stats(request.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Log top 10 slowest functions
        app.logger.info(s.getvalue())
    return response

# Memory profiling example: Annotate critical function
@profile
@app.route('/inventory/add', methods=['POST'])
def add_goods():
    """
    Adds a new item to the inventory.
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

@app.route('/inventory/update/<int:item_id>', methods=['PUT'])
def update_goods(item_id):
    """
    Updates an existing inventory item.
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

@app.route('/inventory/deduct/<int:item_id>', methods=['POST'])
def deduct_goods(item_id):
    """
    Deducts a specified quantity of an inventory item.
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

@app.route('/inventory', methods=['GET'])
def get_inventory():
    """
    Retrieves all items from the inventory.
    """
    items = Inventory.query.all()
    inventory_list = [
        {"id": item.id, "name": item.name, "category": item.category, "price": item.price, "count": item.count}
        for item in items
    ]
    return jsonify(inventory_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
