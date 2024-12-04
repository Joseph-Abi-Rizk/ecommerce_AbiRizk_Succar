import pytest
from customers.app import app, db, Customer
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_customers.db'
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before each test
    with app.app_context():
        db.create_all()

    yield client

    # Drop tables after each test
    with app.app_context():
        db.drop_all()

@pytest.fixture
def auth_header(client):
    """
    Generates an authorization header with a valid JWT token.
    """
    with app.app_context():
        token = create_access_token(identity="testuser@example.com")
    return {"Authorization": f"Bearer {token}"}

def test_register_customer(client):
    """
    Test customer registration functionality.
    """
    response = client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com",
        "password": "securepassword123",
        "age": 30,
        "address": "Test Address",
        "gender": "Other",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert b"Customer registered successfully" in response.data

def test_register_customer_invalid_data(client):
    """
    Test customer registration with missing fields.
    """
    response = client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com"
        # Missing password
    })
    assert response.status_code == 400
    assert b"Username and password are required" in response.data

def test_register_customer_invalid_email(client):
    """
    Test customer registration with invalid email format.
    """
    response = client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "invalid-email",
        "password": "securepassword123"
    })
    assert response.status_code == 400
    assert b"Invalid username format. Use an email address." in response.data

def test_login_success(client):
    """
    Test login functionality with valid credentials.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testlogin@example.com",
        "password": "securepassword123"
    })

    response = client.post('/customers/login', json={
        "username": "testlogin@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    assert b"token" in response.data
    data = response.get_json()
    token = data.get('token')
    assert token is not None

def test_get_customer(client):
    """
    Test fetching customer details.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com",
        "password": "securepassword123"
    })
    response = client.get('/customers/testuser@example.com')
    assert response.status_code == 200
    assert b"testuser@example.com" in response.data

def test_get_customer_not_found(client):
    """
    Test fetching customer details for a non-existing customer.
    """
    response = client.get('/customers/nonexistent@example.com')
    assert response.status_code == 404
    assert b"Customer not found" in response.data

def test_charge_customer(client, auth_header):
    """
    Test charging the wallet of a customer.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com",
        "password": "securepassword123"
    })
    response = client.post('/customers/testuser@example.com/charge', json={
        "amount": 50.0
    }, headers=auth_header)
    assert response.status_code == 200
    assert b"$50.0 charged to testuser@example.com's wallet" in response.data

def test_charge_customer_invalid_amount(client, auth_header):
    """
    Test charging a customer's wallet with an invalid amount.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com",
        "password": "securepassword123"
    })
    response = client.post('/customers/testuser@example.com/charge', json={
        "amount": -10.0
    }, headers=auth_header)
    assert response.status_code == 400
    assert b"Amount must be greater than 0" in response.data

def test_charge_customer_not_found(client, auth_header):
    """
    Test charging a non-existent customer's wallet.
    """
    response = client.post('/customers/nonexistent@example.com/charge', json={
        "amount": 50.0
    }, headers=auth_header)
    assert response.status_code == 404
    assert b"Customer not found" in response.data
