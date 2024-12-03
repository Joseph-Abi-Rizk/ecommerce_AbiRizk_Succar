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
