from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import cProfile
import pstats
from io import StringIO
import logging
from flask_caching import Cache

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\nsucc\\Desktop\\python env\\ecommerce_AbiRizk_Succar\\database\\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YourSecretKey'
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cache = Cache(app)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sales_app.log')
    ]
)

logger = logging.getLogger(__name__)

# Models: Sale, Customer, Inventory
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    wallet_balance = db.Column(db.Float, default=0.0)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    count = db.Column(db.Integer, nullable=False)

# Performance profiling
@app.before_request
def start_profiling():
    request.profiler = cProfile.Profile()
    request.profiler.enable()

@app.after_request
def stop_profiling(response):
    if hasattr(request, 'profiler'):
        request.profiler.disable()
        s = StringIO()
        ps = pstats.Stats(request.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        logger.info(s.getvalue())
    return response

# Routes
@app.route('/sales', methods=['POST'])
@jwt_required()
def process_sale():
    """
    Processes a sale transaction for a customer.
    """
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    item = Inventory.query.get(data['item_id'])

    if not customer or not item:
        return jsonify({"message": "Customer or item not found"}), 404

    if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
        return jsonify({"message": "Quantity must be a positive integer"}), 400

    if customer.wallet_balance < item.price * data['quantity']:
        return jsonify({"message": "Insufficient funds"}), 400

    if item.count < data['quantity']:
        return jsonify({"message": "Insufficient stock"}), 400

    total_price = item.price * data['quantity']
    customer.wallet_balance -= total_price
    item.count -= data['quantity']

    new_sale = Sale(customer_id=customer.id, inventory_id=item.id, quantity=data['quantity'])
    db.session.add(new_sale)
    db.session.commit()

    logger.info(f"Sale processed: {data['username']} bought {data['quantity']} of {item.name}")
    return jsonify({"message": "Sale processed successfully", "remaining_balance": customer.wallet_balance}), 200

@app.route('/sales/goods', methods=['GET'])
def display_goods():
    """
    Displays all available goods in stock.
    """
    items = Inventory.query.filter(Inventory.count > 0).all()
    goods = [{"id": item.id, "name": item.name, "price": item.price, "count": item.count} for item in items]
    return jsonify(goods), 200

@app.route('/sales/history/<username>', methods=['GET'])
@jwt_required()
def purchase_history(username):
    """
    Retrieves the purchase history of a customer.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    sales = Sale.query.filter_by(customer_id=customer.id).all()
    history = [{"item_id": sale.inventory_id, "quantity": sale.quantity, "date": sale.sale_date} for sale in sales]
    return jsonify(history), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
