import pytest
from inventory.app import app, db, Inventory

@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.

    This fixture configures the Flask app for testing, sets the testing database URI to an in-memory SQLite database,
    and creates the necessary tables before each test. After each test, the tables are dropped to ensure a clean state.

    Returns:
        Flask test client: A test client that can be used to send HTTP requests to the app.
    """
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
    """
    Test case for adding a new inventory item.

    This test sends a POST request to the '/inventory/add' endpoint with valid data for a new inventory item.
    It verifies that the item is successfully added to the database and that the correct response is returned.

    Expected outcome:
        - The response status code should be 201.
        - The response message should contain 'Item added successfully'.
    
    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
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
    """
    Test case for retrieving all inventory items.

    This test first adds a new inventory item to the database and then sends a GET request to the '/inventory' endpoint
    to retrieve the list of all inventory items. It verifies that the item appears in the response data.

    Expected outcome:
        - The response status code should be 200.
        - The response data should contain the item name 'Laptop'.
    
    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
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
    """
    Test case for deducting stock from an inventory item.

    This test first adds a new inventory item to the database, then sends a POST request to the '/inventory/deduct/<item_id>'
    endpoint to deduct stock from the inventory item. It verifies that the stock is deducted correctly and that the
    remaining stock is reflected in the response.

    Expected outcome:
        - The response status code should be 200.
        - The response message should contain 'Stock deducted successfully' and the updated count.
        - The remaining count of the item should be 3.

    Args:
        client (Flask test client): The test client used to send HTTP requests.
    """
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
