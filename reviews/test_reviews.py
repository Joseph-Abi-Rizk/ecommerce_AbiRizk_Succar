import pytest
from reviews.app import app, db, Review, Customer, Inventory
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    """
    Initializes the Flask app and sets up a test client for making HTTP requests.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_reviews.db'
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
            wallet_balance=500.0
        )
        db.session.add(user1)

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


@pytest.fixture
def auth_header(client):
    """
    Generates an authorization header with a valid JWT token.
    """
    with app.app_context():
        token = create_access_token(identity="jodim")
    return {"Authorization": f"Bearer {token}"}


def test_submit_review(client, auth_header):
    """
    Test submitting a new review.
    """
    response = client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert response.status_code == 201
    assert b"Review submitted successfully" in response.data


def test_submit_review_invalid_rating(client, auth_header):
    """
    Test submitting a review with an invalid rating.
    """
    response = client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 6,  # Invalid rating
        "comment": "Excellent product!"
    })
    assert response.status_code == 400
    assert b"Rating must be between 1 and 5" in response.data


def test_update_review(client, auth_header):
    """
    Test updating an existing review.
    """
    client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Great product!"
    })
    response = client.put('/reviews/update/1', headers=auth_header, json={
        "rating": 4,
        "comment": "Good product, but not perfect."
    })
    assert response.status_code == 200
    assert b"Review updated successfully" in response.data


def test_delete_review(client, auth_header):
    """
    Test deleting a review.
    """
    client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Good product."
    })
    response = client.delete('/reviews/delete/1', headers=auth_header)
    assert response.status_code == 200
    assert b"Review deleted successfully" in response.data


def test_moderate_review(client, auth_header):
    """
    Test moderating a review.
    """
    client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Good product."
    })
    response = client.post('/reviews/moderate/1', headers=auth_header, json={
        "status": "Approved"
    })
    assert response.status_code == 200
    assert b"Review status updated to Approved" in response.data


def test_get_product_reviews(client, auth_header):
    """
    Test retrieving all reviews for a product.
    """
    client.post('/reviews/submit', headers=auth_header, json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    response = client.get('/reviews/product/1', headers=auth_header)
    assert response.status_code == 200
    assert b"Excellent product!" in response.data

