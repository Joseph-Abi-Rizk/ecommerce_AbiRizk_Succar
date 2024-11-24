import pytest
from reviews.app import app, db, Review, Customer, Inventory

@pytest.fixture
def client():
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
            marital_status="Single"
        )
        user2 = Customer(
            full_name="Nadim Joseph",
            username="nadeph",
            password="nadeph123",
            age=28,
            address="aub",
            gender="Male",
            marital_status="Single"
        )

        # Add users to the database
        db.session.add(user1)
        db.session.add(user2)

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

def test_submit_review(client):
    # Submit review for Laptop by user1 (jodim)
    with app.app_context():
        response = client.post('/reviews/submit', json={
            "username": "jodim",
            "item_id": 1,  # Laptop item ID
            "rating": 5,
            "comment": "Excellent product!"
        })
        assert response.status_code == 201
        assert b"Review submitted successfully" in response.data

        # Verify the review is added in the database
        review = Review.query.filter_by(customer_id=1, inventory_id=1).first()
        assert review.rating == 5
        assert review.comment == "Excellent product!"

def test_update_review(client):
    with app.app_context():
        # Submit a review for user2 (nadeph)
        client.post('/reviews/submit', json={
            "username": "nadeph",
            "item_id": 1,  # Laptop item ID
            "rating": 4,
            "comment": "Good product"
        })

        # Get the review ID (assume ID 1 for simplicity)
        review_id = 1

        # Update the review
        response = client.put(f'/reviews/update/{review_id}', json={
            "rating": 3,
            "comment": "Decent product, but could be better"
        })
        assert response.status_code == 200
        assert b"Review updated successfully" in response.data

        # Verify the review is updated in the database
        review = Review.query.get(review_id)
        assert review.rating == 3
        assert review.comment == "Decent product, but could be better"

def test_get_product_reviews(client):
    # Submit reviews for Laptop (item_id = 1)
    client.post('/reviews/submit', json={
        "username": "jodim",
        "item_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    client.post('/reviews/submit', json={
        "username": "nadeph",
        "item_id": 1,
        "rating": 4,
        "comment": "Good product, but a bit pricey"
    })

    response = client.get('/reviews/product/1')
    assert response.status_code == 200
    assert b"Excellent product!" in response.data
    assert b"Good product, but a bit pricey" in response.data
