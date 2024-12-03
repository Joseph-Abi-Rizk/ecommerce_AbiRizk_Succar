import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import re
import logging
from flask_caching import Cache

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'NadimandJoseph'
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
        logging.FileHandler('customers_app.log')  # Logs saved to app.log
    ]
)

logger = logging.getLogger(__name__)

# Customer Model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    wallet_balance = db.Column(db.Float, default=0.0)

def validate_email(username):
    """Validates email format for username."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, username)

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

# Health Check
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if the database is up
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "failed"}), 500

# Register a customer
@profile
@app.route('/customers/register', methods=['POST'])
def register_customer():
    """
    Registers a new customer.
    """
    data = request.get_json()

    # Validate required fields
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    if not validate_email(data['username']):
        return jsonify({"message": "Invalid username format. Use an email address."}), 400

    # Check if the username is unique
    if Customer.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already taken"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password'], method='bcrypt')

    # Create and add new customer
    new_customer = Customer(
        full_name=data.get('full_name'),
        username=data['username'],
        password=hashed_password,
        age=data.get('age'),
        address=data.get('address'),
        gender=data.get('gender'),
        marital_status=data.get('marital_status'),
    )
    db.session.add(new_customer)
    db.session.commit()
    logger.info(f"New customer registered: {data['username']}")
    return jsonify({"message": "Customer registered successfully"}), 201

# Login a customer
@app.route('/customers/login', methods=['POST'])
def login():
    """
    Authenticates a user and returns a JWT token.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    customer = Customer.query.filter_by(username=username).first()
    if not customer or not check_password_hash(customer.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    token = create_access_token(identity=username)
    logger.info(f"User logged in: {username}")
    return jsonify({"token": token}), 200

# Charge customer's wallet
@app.route('/customers/<username>/charge', methods=['POST'])
@jwt_required()
def charge_customer(username):
    """
    Charges a customer's wallet with a specified amount.
    """
    data = request.get_json()
    amount = data.get('amount', 0)
    customer = Customer.query.filter_by(username=username).first()

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    if amount <= 0:
        return jsonify({"message": "Amount must be greater than 0"}), 400

    customer.wallet_balance += amount
    db.session.commit()
    logger.info(f"${amount} charged to {username}'s wallet")
    return jsonify({"message": f"${amount} charged to {username}'s wallet"}), 200

# Get all customers
@app.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Fetches all customers.
    """
    customers = Customer.query.all()
    customer_list = [{"id": customer.id, "username": customer.username, "full_name": customer.full_name} for customer in customers]
    return jsonify(customer_list)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
