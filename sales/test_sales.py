import pytest
from sales.app import app, db, Sale, Customer, Inventory
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_sales.db'
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

        user1 = Customer(
            full_name="Joseph Nadim",
            username="jodim",
            password="jodim123",
            age=21,
            address="hamra bliss",
            gender="Male",
            marital_status="Single",
            wallet_balance=1000.0
        )
        db.session.add(user1)

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

    with app.app_context():
        db.drop_all()

@pytest.fixture
def auth_header(client):
    """
    Generates an authorization header with a valid JWT token.
    """
    with app.app_context():
        token = create_access_token(identity="jodim")
    return {"Authorization": f"Bearer {token}"}

def test_process_sale(client, auth_header):
    """
    Test processing a sale transaction.
    """
    with app.app_context():
        response = client.post('/sales', headers=auth_header, json={
            "username": "jodim",
            "item_id": 1,
            "quantity": 1
        })
        assert response.status_code == 200
        assert b"Sale processed successfully" in response.data

def test_process_sale_invalid_quantity(client, auth_header):
    """
    Test processing a sale with an invalid quantity.
    """
    with app.app_context():
        response = client.post('/sales', headers=auth_header, json={
            "username": "jodim",
            "item_id": 1,
            "quantity": -1
        })
        assert response.status_code == 400
        assert b"Quantity must be a positive integer" in response.data

def test_display_goods(client):
    """
    Test displaying available goods.
    """
    with app.app_context():
        response = client.get('/sales/goods')
        assert response.status_code == 200
        assert b"Laptop" in response.data

def test_purchase_history(client, auth_header):
    """
    Test retrieving a customer's purchase history.
    """
    with app.app_context():
        client.post('/sales', headers=auth_header, json={
            "username": "jodim",
            "item_id": 1,
            "quantity": 1
        })
        response = client.get('/sales/history/jodim', headers=auth_header)
        assert response.status_code == 200
        assert b"1" in response.data

def test_cache(client):
    """
    Test caching functionality.
    """
    with app.app_context():
        response1 = client.get('/sales/goods')
        response2 = client.get('/sales/goods')

        assert response1.data == response2.data
        assert response2.status_code == 200
        assert b"Laptop" in response2.data
