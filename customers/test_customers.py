import pytest
from customers.app import app, db

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.

    This fixture configures the Flask app for testing, sets the testing database URI to an in-memory SQLite database,
    and creates the necessary tables before each test. After each test, the tables are dropped to ensure a clean state.

    Returns:
        Flask test client: A test client that can be used to send HTTP requests to the app.
    """
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
    """
    Test case for customer registration.

    This test sends a POST request to the '/customers/register' endpoint with valid customer details.
    It verifies that the customer is successfully registered and that the response status code is 201 (Created).

    Expected outcome:
        - The response status code should be 201.
        - The response message should contain 'Customer registered successfully'.
    
    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
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
    """
    Test case for handling duplicate usernames during customer registration.

    This test first registers a customer with the username 'jodim', then tries to register a second customer
    with the same username. It verifies that the second attempt returns a 400 status code and the message
    'Username already taken'.

    Expected outcome:
        - The first registration should succeed with a status code of 201.
        - The second registration should fail with a status code of 400 and a message 'Username already taken'.

    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
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
    """
    Test case for retrieving all customers.

    This test registers a customer and then sends a GET request to the '/customers' endpoint to retrieve a list of all customers.
    It verifies that the registered customer's username appears in the response data.

    Expected outcome:
        - The response status code should be 200.
        - The response data should contain the username 'jodim'.

    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
    
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
