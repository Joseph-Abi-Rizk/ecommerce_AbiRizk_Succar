from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database.models import db,Sale,Customer,Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



# Display available goods
@app.route('/sales/goods', methods=['GET'])
def display_goods():
    """
    Displays all available goods (items) in stock.

    This function retrieves all items from the inventory where the stock count is greater than zero
    and returns them with their basic details such as name, price, and available stock.

    Arguments:
        None

    Returns:
        JSON response containing a list of available items in stock with their details.
        - Example: [{"id": 1, "name": "Laptop", "price": 1000.0, "count": 10}]
    """
    items = Inventory.query.filter(Inventory.count > 0).all()
    goods = [{"id": item.id, "name": item.name, "price": item.price, "count": item.count} for item in items]
    return jsonify(goods)

# Get goods details
@app.route('/sales/goods/<int:item_id>', methods=['GET'])
def goods_details(item_id):
    """
    Retrieves the details of a specific item in the inventory.

    This function accepts an item ID and returns detailed information about the item, including its name,
    category, price, description, and available stock.

    Arguments:
        item_id (int): The ID of the item to retrieve details for.

    Returns:
        JSON response containing the details of the specified item.
        - Success: Item details in JSON format
        - Failure: {"message": "Item not found"}, status code 404
    """
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
    """
    Processes a sale transaction for a customer.

    This function handles the sale process by checking if the customer has enough funds to make the purchase
    and if the product has sufficient stock. If the sale is valid, the inventory and customer wallet are updated,
    and a sale record is created.

    Arguments:
        None (data is expected in the request body)

    Returns:
        JSON response with success or error message:
            - Success: {"message": "Sale processed successfully", "remaining_balance": <remaining_balance>}, status code 200
            - Failure: {"message": "Customer or item not found"} or {"message": "Insufficient funds"} or {"message": "Insufficient stock"}, status code 404, 400, or 400
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

# Get purchase history
@app.route('/sales/history/<username>', methods=['GET'])
def purchase_history(username):
    """
    Retrieves the purchase history of a customer.

    This function accepts a customer's username and retrieves all the sales made by that customer,
    including the item IDs, quantities, and sale dates.

    Arguments:
        username (str): The username of the customer whose purchase history is being retrieved.

    Returns:
        JSON response containing the customer's purchase history.
        - Success: A list of purchases in JSON format, status code 200
        - Failure: {"message": "Customer not found"}, status code 404
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    sales = Sale.query.filter_by(customer_id=customer.id).all()
    history = [
        {"item_id": sale.inventory_id, "quantity": sale.quantity,  "date": sale.sale_date}
        for sale in sales
    ]
    return jsonify(history)

if __name__ == '__main__':
    """
    Runs the Flask application.

    Starts the Flask web server on host 0.0.0.0 and port 5003 in debug mode.

    Arguments:
        None

    Returns:
        None
    """
    app.run(debug=True, host='0.0.0.0', port=5003)
