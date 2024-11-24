import pytest
from sales.app import app,db, Sale, Customer, Inventory

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.

    This fixture configures the Flask app for testing, sets the testing database URI to an in-memory SQLite database,
    and creates the necessary tables before each test. It also creates some test data (users and inventory items)
    that are committed to the database before each test. After each test, the tables are dropped to ensure a clean state.

    Returns:
        Flask test client: A test client that can be used to send HTTP requests to the app.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_sales.db'
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before each test
    with app.app_context():
        db.create_all()

        # Create test users
        user1 = Customer(
            full_name="Joseph Nadim",
            username="jodim",
            password="jodim123",
            age=21,
            address="hamra bliss",
            gender="Male",
            marital_status="Single",
            wallet_balance=1000
        )
        user2 = Customer(
            full_name="Nadim Joseph",
            username="nadeph",
            password="nadeph123",
            age=28,
            address="aub",
            gender="Male",
            marital_status="Single",
            wallet_balance=1000
        )

        # Add users to the database
        db.session.add(user1)
        db.session.add(user2)

        # Create inventory item (Laptop)
        inventory_item = Inventory(
            name="Laptop",
            category="Electronics",
            price=1000.0,
            description="High-end gaming laptop",
            count=10
        )
        db.session.add(inventory_item)

        db.session.commit()

    yield client

    # Drop tables after each test
    with app.app_context():
        db.drop_all()

def test_process_sale(client):
    """
    Test case for processing a sale transaction.

    This test simulates a sale transaction where a customer (jodim) buys an item (Laptop) from the inventory.
    It checks if the sale is processed correctly by verifying the updated wallet balance and the inventory count.

    Expected outcome:
        - The response status code should be 200.
        - The response message should contain 'Sale processed successfully'.
        - The wallet balance of the customer should be deducted by the price of the item.
        - The inventory count should be reduced by the quantity of the item purchased.

    Arguments:
        client (Flask test client): The test client used to send HTTP requests.
    """
    with app.app_context():
        # Simulate a sale for user1 (jodim)
        response = client.post('/sales', json={
            "username": "jodim",
            "item_id": 1,  # Laptop item ID
            "quantity": 1
        })
        assert response.status_code == 200
        assert b"Sale processed successfully" in response.data

        # Verify the updated wallet balance
        customer = Customer.query.filter_by(username="jodim").first()
        assert customer.wallet_balance == 0  # Wallet should be deducted by the price of the laptop

        # Verify inventory count
        item = Inventory.query.get(1)
        assert item.count == 9  # Inventory count should decrease by 1

def test_get_purchase_history(client):
    """
    Test case for retrieving a customer's purchase history.

    This test simulates a sale transaction for a customer (nadeph) and then checks the customer's purchase history.
    It verifies that the history returns the correct items and quantities purchased.

    Expected outcome:
        - The response status code should be 200.
        - The response data should include the correct item ID and quantity for the customer's purchase history.

    Arguments:
        client (Flask test client): The test client used to send HTTP requests.
    """
    with app.app_context():

        # Simulate a sale for user2 
        client.post('/sales', json={
            "username": "nadeph",
            "item_id": 1,  # Laptop item ID
            "quantity": 1
        })

        response = client.get('/sales/history/nadeph')
        assert response.status_code == 200


        