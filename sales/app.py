import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
from flask import Flask, request, jsonify
from database.models import db, Sale, Customer, Inventory

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
@app.route('/sales', methods=['POST'])
def process_sale():
    """
    Processes a sale transaction for a customer.
    """
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    item = Inventory.query.get(data['item_id'])

    if not customer or not item:
        return jsonify({"message": "Customer or item not found"}), 404

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

    return jsonify({"message": "Sale processed successfully", "remaining_balance": customer.wallet_balance})

@app.route('/sales/goods', methods=['GET'])
def display_goods():
    """
    Displays all available goods (items) in stock.
    """
    items = Inventory.query.filter(Inventory.count > 0).all()
    goods = [{"id": item.id, "name": item.name, "price": item.price, "count": item.count} for item in items]
    return jsonify(goods)

@app.route('/sales/history/<username>', methods=['GET'])
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
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
