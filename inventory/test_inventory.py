import pytest
from inventory.app import app, db, Inventory, User
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_inventory.db'
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before each test
    with app.app_context():
        db.create_all()
        # Add a test user
        user = User(username="testuser", password="testpassword")
        db.session.add(user)
        db.session.commit()

    yield client

    # Drop tables after each test
    with app.app_context():
        db.drop_all()


@pytest.fixture
def auth_header(client):
    """
    Generates an authorization header with a valid JWT token.
    """
    response = client.post('/inventory/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.get_json().get("token")
    return {"Authorization": f"Bearer {token}"}


def test_login_success(client):
    """
    Test login functionality with valid credentials.
    """
    response = client.post('/inventory/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_failure(client):
    """
    Test login functionality with invalid credentials.
    """
    response = client.post('/inventory/login', json={
        "username": "wronguser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_add_goods_protected(client):
    """
    Test that the add goods endpoint is protected.
    """
    response = client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })
    assert response.status_code == 401
    assert b"Missing Authorization Header" in response.data


def test_add_goods(client, auth_header):
    """
    Test adding a new inventory item with a valid token.
    """
    response = client.post('/inventory/add', headers=auth_header, json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })
    assert response.status_code == 201
    assert b"Item added successfully" in response.data


def test_get_inventory(client, auth_header):
    """
    Test retrieving all inventory items.
    """
    client.post('/inventory/add', headers=auth_header, json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })
    response = client.get('/inventory')
    assert response.status_code == 200
    assert b"Laptop" in response.data


def test_update_goods_protected(client):
    """
    Test that the update goods endpoint is protected.
    """
    response = client.put('/inventory/update/1', json={"price": 1200.0, "count": 10})
    assert response.status_code == 401
    assert b"Missing Authorization Header" in response.data


def test_update_goods(client, auth_header):
    """
    Test updating an inventory item with a valid token.
    """
    client.post('/inventory/add', headers=auth_header, json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })

    response = client.put('/inventory/update/1', headers=auth_header, json={"price": 1200.0, "count": 10})
    assert response.status_code == 200
    assert b"Item updated successfully" in response.data


def test_deduct_goods_protected(client):
    """
    Test that the deduct goods endpoint is protected.
    """
    response = client.post('/inventory/deduct/1', json={"count": 2})
    assert response.status_code == 401
    assert b"Missing Authorization Header" in response.data


def test_deduct_goods(client, auth_header):
    """
    Test deducting stock from an inventory item with a valid token.
    """
    client.post('/inventory/add', headers=auth_header, json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })

    response = client.post('/inventory/deduct/1', headers=auth_header, json={"count": 2})
    assert response.status_code == 200
    assert b"Stock deducted successfully" in response.data
    assert b"3" in response.data  # Remaining count should be 3
