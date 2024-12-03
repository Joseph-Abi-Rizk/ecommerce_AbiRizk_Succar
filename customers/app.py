import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from database.models import db, Customer

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'NadimandJoseph'

db.init_app(app)
jwt = JWTManager(app)

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
@app.route('/customers/register', methods=['POST'])
def register_customer():
    """
    Registers a new customer.
    """
    data = request.get_json()

    # Validate input data
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    # Check if the username is unique
    if Customer.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already taken"}), 400

    # Create and add new customer
    new_customer = Customer(
        full_name=data['full_name'],
        username=data['username'],
        password=data['password'],
        age=data.get('age'),
        address=data.get('address'),
        gender=data.get('gender'),
        marital_status=data.get('marital_status'),
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer registered successfully"}), 201

@app.route('/customers', methods=['GET'])
def get_customers():
    """
    Fetches all customers.
    """
    customers = Customer.query.all()
    customer_list = [{"id": customer.id, "username": customer.username, "full_name": customer.full_name} for customer in customers]
    return jsonify(customer_list)

@app.route('/customers/<username>', methods=['GET'])
def get_customer_by_username(username):
    """
    Fetches a customer by username.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    return jsonify({
        "username": customer.username,
        "full_name": customer.full_name,
        "age": customer.age,
        "address": customer.address,
        "gender": customer.gender,
        "marital_status": customer.marital_status,
        "wallet_balance": customer.wallet_balance
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
