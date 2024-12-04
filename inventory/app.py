from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
import logging
from flask_caching import Cache

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\nsucc\\Desktop\\python env\\ecommerce_AbiRizk_Succar\\database\\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YourSecretKey'  # Change this to a secure key
app.config['CACHE_TYPE'] = 'simple'  # You can change this to 'redis' for better performance
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cache = Cache(app)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Outputs logs to console
        logging.FileHandler('inventory_app.log')  # Logs saved to app.log
    ]
)

logger = logging.getLogger(__name__)


# User Model for Authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Should be hashed in a real app

# Inventory Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    count = db.Column(db.Integer, nullable=False)

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



# Routes
@app.route('/inventory/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JWT token.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    token = create_access_token(identity=username)
    logger.info(f"User logged in: {username}")
    return jsonify({"token": token}), 200

@profile
@app.route('/inventory/add', methods=['POST'])
@jwt_required()
def add_goods():
    """
    Adds a new item to the inventory.
    """
    data = request.get_json()

    # Validation
    if not all(key in data for key in ['name', 'category', 'price', 'count']):
        return jsonify({"message": "Missing required fields"}), 400
    if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
        return jsonify({"message": "Price must be a positive number"}), 400
    if not isinstance(data['count'], int) or data['count'] < 0:
        return jsonify({"message": "Count must be a non-negative integer"}), 400

    # Create new item
    new_item = Inventory(
        name=data['name'],
        category=data['category'],
        price=data['price'],
        description=data.get('description', ''),
        count=data['count']
    )
    db.session.add(new_item)
    db.session.commit()
    logger.info(f"New item added: {data['name']} (Category: {data['category']})")
    return jsonify({"message": "Item added successfully"}), 201

@app.route('/inventory/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_goods(item_id):
    """
    Updates an existing inventory item.
    """
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json()
    if 'price' in data and (not isinstance(data['price'], (int, float)) or data['price'] <= 0):
        return jsonify({"message": "Price must be a positive number"}), 400
    if 'count' in data and (not isinstance(data['count'], int) or data['count'] < 0):
        return jsonify({"message": "Count must be a non-negative integer"}), 400

    # Update fields
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)

    db.session.commit()
    logger.info(f"Item updated: {item.name}")
    return jsonify({"message": "Item updated successfully"}), 200

@app.route('/inventory/deduct/<int:item_id>', methods=['POST'])
@jwt_required()
def deduct_goods(item_id):
    """
    Deducts a specified quantity of an inventory item.
    """
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json()
    if 'count' not in data or not isinstance(data['count'], int) or data['count'] <= 0:
        return jsonify({"message": "Count must be a positive integer"}), 400
    if item.count < data['count']:
        return jsonify({"message": "Insufficient stock"}), 400

    item.count -= data['count']
    db.session.commit()
    logger.info(f"Stock deducted: {item.name} | Remaining stock: {item.count}")
    return jsonify({"message": "Stock deducted successfully", "remaining_count": item.count}), 200

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
    return jsonify(inventory_list), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
        # Add a test user
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="admin123"))
            db.session.commit()

    app.run(debug=True, host='0.0.0.0', port=5002)
