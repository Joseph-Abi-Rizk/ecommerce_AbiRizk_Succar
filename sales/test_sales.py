import pytest
from sales.app import app, db, Sale, Customer, Inventory

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.
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
    Test processing a sale transaction.
    """
    response = client.post('/sales', json={
        "username": "jodim",
        "item_id": 1,  # Laptop item ID
        "quantity": 1
    })
    assert response.status_code == 200
    assert b"Sale processed successfully" in response.data

    # Verify the updated wallet balance
    customer = Customer.query.filter_by(username="jodim").first()
    assert customer.wallet_balance == 0

    # Verify inventory count
    item = Inventory.query.get(1)
    assert item.count == 9

def test_display_goods(client):
    """
    Test displaying available goods.
    """
    response = client.get('/sales/goods')
    assert response.status_code == 200
    assert b"Laptop" in response.data

def test_get_purchase_history(client):
    """
    Test retrieving a customer's purchase history.
    """
    client.post('/sales', json={
        "username": "nadeph",
        "item_id": 1,  # Laptop item ID
        "quantity": 1
    })

    response = client.get('/sales/history/nadeph')
    assert response.status_code == 200
    assert b"1" in response.data
