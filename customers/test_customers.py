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
    token = create_access_token(identity="testuser@example.com")
    return {"Authorization": f"Bearer {token}"}


def test_password_hashing(client):
    """
    Test that passwords are hashed and not stored in plain text.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser@example.com",
        "password": "securepassword123",
        "age": 30,
        "address": "Test Address",
        "gender": "Other",
        "marital_status": "Single"
    })
    with app.app_context():
        customer = Customer.query.filter_by(username="testuser@example.com").first()
        assert customer is not None
        assert customer.password != "securepassword123"  # Ensure password is hashed


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


def test_login_failure(client):
    """
    Test login functionality with invalid credentials.
    """
    response = client.post('/customers/login', json={
        "username": "wronguser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_register_duplicate_username(client):
    """
    Test registering a new customer with an already taken username.
    """
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "duplicate@example.com",
        "password": "password123"
    })
    response = client.post('/customers/register', json={
        "full_name": "Another User",
        "username": "duplicate@example.com",
        "password": "password456"
    })
    assert response.status_code == 400
    assert b"Username already taken" in response.data


def test_get_all_customers(client):
    """
    Test retrieving all registered customers.
    """
    client.post('/customers/register', json={
        "full_name": "User One",
        "username": "userone@example.com",
        "password": "password1"
    })
    client.post('/customers/register', json={
        "full_name": "User Two",
        "username": "usertwo@example.com",
        "password": "password2"
    })

    response = client.get('/customers')
    assert response.status_code == 200
    assert b"userone@example.com" in response.data
    assert b"usertwo@example.com" in response.data


def test_delete_customer(client, auth_header):
    """
    Test deleting a customer by username.
    """
    client.post('/customers/register', json={
        "full_name": "Delete Me",
        "username": "deleteme@example.com",
        "password": "password123"
    })
    response = client.delete('/customers/deleteme@example.com', headers=auth_header)
    assert response.status_code == 200
    assert b"Customer deleted successfully" in response.data


def test_update_customer(client, auth_header):
    """
    Test updating customer information.
    """
    client.post('/customers/register', json={
        "full_name": "Original Name",
        "username": "updateme@example.com",
        "password": "password123"
    })
    response = client.put('/customers/updateme@example.com', headers=auth_header, json={
        "full_name": "Updated Name",
        "age": 35
    })
    assert response.status_code == 200
    assert b"Customer updated successfully" in response.data


def test_charge_customer_wallet(client, auth_header):
    """
    Test charging a customer's wallet.
    """
    client.post('/customers/register', json={
        "full_name": "Wallet User",
        "username": "walletuser@example.com",
        "password": "password123"
    })

    response = client.post('/customers/walletuser@example.com/charge', headers=auth_header, json={
        "amount": 100
    })
    assert response.status_code == 200
    assert b"100 charged to walletuser@example.com's wallet" in response.data


def test_deduct_customer_wallet(client, auth_header):
    """
    Test deducting money from a customer's wallet.
    """
    client.post('/customers/register', json={
        "full_name": "Deduction User",
        "username": "deductionuser@example.com",
        "password": "password123"
    })
    client.post('/customers/deductionuser@example.com/charge', headers=auth_header, json={
        "amount": 200
    })

    response = client.post('/customers/deductionuser@example.com/deduct', headers=auth_header, json={
        "amount": 50
    })
    assert response.status_code == 200
    assert b"50 deducted from deductionuser@example.com's wallet" in response.data
