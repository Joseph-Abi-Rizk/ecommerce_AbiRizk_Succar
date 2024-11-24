from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database.models import db,Sale,Customer,Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



# Display available goods
@app.route('/sales/goods', methods=['GET'])
def display_goods():
    items = Inventory.query.filter(Inventory.count > 0).all()
    goods = [{"id": item.id, "name": item.name, "price": item.price, "count": item.count} for item in items]
    return jsonify(goods)

# Get goods details
@app.route('/sales/goods/<int:item_id>', methods=['GET'])
def goods_details(item_id):
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    return jsonify({
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": item.price,
        "description": item.description,
        "count": item.count
    })

# Process a sale
@app.route('/sales', methods=['POST'])
def process_sale():
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
    new_sale = Sale(customer_id=customer.id, inventory_id=item.id, quantity=data['quantity'], total_price=total_price)
    db.session.add(new_sale)
    db.session.commit()

    return jsonify({"message": "Sale processed successfully", "remaining_balance": customer.wallet_balance})

# Get purchase history
@app.route('/sales/history/<username>', methods=['GET'])
def purchase_history(username):
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    sales = Sale.query.filter_by(customer_id=customer.id).all()
    history = [
        {"item_id": sale.inventory_id, "quantity": sale.quantity, "total_price": sale.total_price, "date": sale.sale_date}
        for sale in sales
    ]
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
