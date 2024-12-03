from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import cProfile
import pstats
from io import StringIO
from memory_profiler import profile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YourSecretKey'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models: Sale, Customer, Inventory

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
        app.logger.info(s.getvalue())
    return response

@profile
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

    # Validate quantity
    if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
        return jsonify({"message": "Quantity must be a positive integer"}), 400

    if customer.wallet_balance < item.price * data['quantity']:
        return jsonify({"message": "Insufficient funds"}), 400

    if item.count < data['quantity']:
        return jsonify({"message": "Insufficient stock"}), 400

    # Update inventory and customer wallet
    total_price = item.price * data['quantity']
    customer.wallet_balance -= total_price
    item.count -= data['quantity']

    # Record the sale
    new_sale = Sale(customer_id=customer.id, inventory_id=item.id, quantity=data['quantity'])
    db.session.add(new_sale)
    db.session.commit()

    return jsonify({"message": "Sale processed successfully", "remaining_balance": customer.wallet_balance}), 200

@app.route('/sales/goods', methods=['GET'])
def display_goods():
    """
    Displays all available goods (items) in stock.
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
    history = [
        {"item_id": sale.inventory_id, "quantity": sale.quantity, "date": sale.sale_date}
        for sale in sales
    ]
    return jsonify(history), 200
