import pytest
from inventory.app import app, db, Inventory

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_inventory.db'
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before each test
    with app.app_context():
        db.create_all()

    yield client

    # Drop tables after each test
    with app.app_context():
        db.drop_all()

def test_add_goods(client):
    response = client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })
    assert response.status_code == 201
    assert b"Item added successfully" in response.data

def test_get_inventory(client):
    client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })
    response = client.get('/inventory')
    assert response.status_code == 200
    assert b"Laptop" in response.data

def test_deduct_goods(client):
    client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "Electronics",
        "price": 1000.0,
        "description": "A high-performance laptop",
        "count": 5
    })

    response = client.post('/inventory/deduct/1', json={"count": 2})
    assert response.status_code == 200
    assert b"Stock deducted successfully" in response.data
    assert b"3" in response.data  # Remaining count should be 3
