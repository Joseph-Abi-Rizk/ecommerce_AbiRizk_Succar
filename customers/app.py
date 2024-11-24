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

# Customer registration endpoint
@app.route('/customers/register', methods=['POST'])
def register_customer():
    """
    Registers a new customer.

    Validates the provided data, checks if the username is unique, 
    and creates a new customer record in the database.

    Arguments:
        None (data is expected in the request body)

    Returns:
        JSON response with a success message or error message.
        - Success: {"message": "Customer registered successfully"}, status code 201
        - Failure: {"message": "Username already taken"} or {"message": "Username and password are required"}, status code 400
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

# Get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    """
    Fetches all customers from the database.

    Arguments:
        None

    Returns:
        JSON list of customers with basic details (id, username, full_name).
    """
    customers = Customer.query.all()
    customer_list = [{"id": customer.id, "username": customer.username, "full_name": customer.full_name} for customer in customers]
    return jsonify(customer_list)

# Get customer by username
@app.route('/customers/<username>', methods=['GET'])
def get_customer_by_username(username):
    """
    Fetches the customer details by their username.

    Arguments:
        username (str): The username of the customer to retrieve.

    Returns:
        JSON response with customer details if found, else error message.
        - Success: Customer details in JSON format, status code 200
        - Failure: {"message": "Customer not found"}, status code 404
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

# Update customer details
@app.route('/customers/<username>', methods=['PUT'])
def update_customer(username):
    """
    Updates the details of an existing customer.

    Arguments:
        username (str): The username of the customer to update.
    
    Request Data:
        JSON data with fields that need to be updated (e.g., full_name, age, etc.)

    Returns:
        JSON response with success message or error message.
        - Success: {"message": "Customer updated successfully"}, status code 200
        - Failure: {"message": "Customer not found"}, status code 404
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    data = request.get_json()
    if data.get('full_name'):
        customer.full_name = data['full_name']
    if data.get('age'):
        customer.age = data['age']
    if data.get('address'):
        customer.address = data['address']
    if data.get('gender'):
        customer.gender = data['gender']
    if data.get('marital_status'):
        customer.marital_status = data['marital_status']

    db.session.commit()
    return jsonify({"message": "Customer updated successfully"})

# Delete customer
@app.route('/customers/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Deletes a customer by username.

    Arguments:
        username (str): The username of the customer to delete.
    
    Returns:
        JSON response with success message or error message.
        - Success: {"message": "Customer deleted successfully"}, status code 200
        - Failure: {"message": "Customer not found"}, status code 404
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"})

# Charge customer's wallet
@app.route('/customers/charge', methods=['POST'])
def charge_customer():
    """
    Charges a specified amount to a customer's wallet.

    Arguments:
        JSON data with `username` and `amount` to charge.
    
    Returns:
        JSON response with updated wallet balance or error message.
        - Success: {"message": "Wallet charged successfully", "wallet_balance": <new_balance>}, status code 200
        - Failure: {"message": "Customer not found"}, status code 404
    """
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    customer.wallet_balance += data['amount']
    db.session.commit()
    return jsonify({"message": "Wallet charged successfully", "wallet_balance": customer.wallet_balance})

# Deduct from customer's wallet
@app.route('/customers/deduct', methods=['POST'])
def deduct_from_wallet():
    """
    Deducts a specified amount from a customer's wallet.

    Arguments:
        JSON data with `username` and `amount` to deduct.
    
    Returns:
        JSON response with updated wallet balance or error message.
        - Success: {"message": "Amount deducted", "wallet_balance": <new_balance>}, status code 200
        - Failure: {"message": "Customer not found"} or {"message": "Insufficient funds"}, status code 404 or 400
    """
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    if customer.wallet_balance < data['amount']:
        return jsonify({"message": "Insufficient funds"}), 400

    customer.wallet_balance -= data['amount']
    db.session.commit()
    return jsonify({"message": "Amount deducted", "wallet_balance": customer.wallet_balance})


if __name__ == '__main__':
    """
    Runs the Flask application.
    
    Starts the Flask web server on host 0.0.0.0 and port 5001 in debug mode.

    Arguments:
        None
    
    Returns:
        None
    """
    app.run(debug=True, host='0.0.0.0', port=5001)