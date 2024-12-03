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

def test_health_check(client):
    """
    Test the health check endpoint.
    """
    response = client.get('/health')
    assert response.status_code == 200
    assert b"healthy" in response.data

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

def test_customer_cache(client):
    """
    Test caching functionality for customer data.
    """
    response1 = client.get('/customers/testuser@example.com')
    response2 = client.get('/customers/testuser@example.com')  # Should hit the cache
    
    # Verify that both requests return the same data
    assert response1.data == response2.data
    assert response2.status_code == 200

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

