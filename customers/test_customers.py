import pytest
from customers.app import app, db

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before each test
    with app.app_context():
        db.create_all()

    yield client

    # Drop tables after each test
    with app.app_context():
        db.drop_all()

def test_register_customer(client):
    response = client.post('/customers/register', json={
        "full_name": "Joseph Nadim",
        "username": "jodim",
        "password": "jodim123",
        "age": 21,
        "address": "hamra bliss",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert b"Customer registered successfully" in response.data

def test_duplicate_username(client):
    # Register first customer
    client.post('/customers/register', json={
        "full_name": "Joseph Nadim",
        "username": "jodim",
        "password": "jodim123",
        "age": 21,
        "address": "hamra bliss",
        "gender": "Male",
        "marital_status": "Single"
    })

    # Attempt to register second customer with the same username
    response = client.post('/customers/register', json={
        "full_name": "Nadim Joseph",
        "username": "jodim",
        "password": "nadeph123",
        "age": 28,
        "address": "aub",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert b"Username already taken" in response.data

def test_get_all_customers(client):
    client.post('/customers/register', json={
        "full_name": "Joseph Nadim",
        "username": "jodim",
        "password": "jodim123",
        "age": 21,
        "address": "hamra bliss",
        "gender": "Male",
        "marital_status": "Single"
    })

    response = client.get('/customers')
    assert response.status_code == 200
    assert b"jodim" in response.data
