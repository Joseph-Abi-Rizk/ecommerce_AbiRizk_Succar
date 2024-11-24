from flask import Flask, request, jsonify
from database.models import db, Review, Customer, Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Submit a new review
@app.route('/reviews/submit', methods=['POST'])
def submit_review():
    """
    Submits a new review for a product by a customer.

    This function accepts a POST request containing customer details, product details (item_id), 
    rating, and an optional comment. It verifies that the customer and product exist, creates a new 
    review, and saves it to the database.

    Arguments:
        None (data is expected in the request body)

    Returns:
        JSON response with success or error message:
            - Success: {"message": "Review submitted successfully"}, status code 201
            - Failure: {"message": "Customer or item not found"}, status code 404
    """
    data = request.get_json()

    # Check if customer and item exist
    customer = Customer.query.filter_by(username=data['username']).first()
    item = Inventory.query.get(data['item_id'])

    if not customer or not item:
        return jsonify({"message": "Customer or item not found"}), 404

    # Create and save the review
    new_review = Review(
        customer_id=customer.id,
        inventory_id=item.id,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review submitted successfully"}), 201

# Update a review
@app.route('/reviews/update/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Updates an existing review.

    This function allows a customer or an administrator to update a review's rating or comment.
    It checks if the review exists and updates the provided fields.

    Arguments:
        review_id (int): The ID of the review to be updated.
    
    Request Data:
        JSON containing optional fields to update (rating, comment).

    Returns:
        JSON response with success or error message:
            - Success: {"message": "Review updated successfully"}, status code 200
            - Failure: {"message": "Review not found"}, status code 404
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json()
    if 'rating' in data:
        review.rating = data['rating']
    if 'comment' in data:
        review.comment = data['comment']

    db.session.commit()
    return jsonify({"message": "Review updated successfully"})

# Delete a review
@app.route('/reviews/delete/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Deletes a review from the database.

    This function handles the deletion of a review by its ID. It checks if the review exists,
    and if it does, it removes it from the database.

    Arguments:
        review_id (int): The ID of the review to be deleted.
    
    Returns:
        JSON response with success or error message:
            - Success: {"message": "Review deleted successfully"}, status code 200
            - Failure: {"message": "Review not found"}, status code 404
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"})

# Get all reviews for a product
@app.route('/reviews/product/<int:item_id>', methods=['GET'])
def get_product_reviews(item_id):
    """
    Retrieves all reviews for a specific product.

    This function accepts a GET request with the product ID (item_id) and returns all reviews
    for that product. If no reviews are found, it returns an appropriate message.

    Arguments:
        item_id (int): The ID of the product to fetch reviews for.
    
    Returns:
        JSON response with a list of reviews or error message:
            - Success: A list of reviews for the product, status code 200
            - Failure: {"message": "No reviews found for this product"}, status code 404
    """
    reviews = Review.query.filter_by(inventory_id=item_id).all()
    if not reviews:
        return jsonify({"message": "No reviews found for this product"}), 404

    reviews_list = [
        {"id": review.id, "customer_id": review.customer_id, "rating": review.rating, "comment": review.comment, "status": review.status}
        for review in reviews
    ]
    return jsonify(reviews_list)

# Moderate a review (approve or reject)
@app.route('/reviews/moderate/<int:review_id>', methods=['POST'])
def moderate_review(review_id):
    """
    Moderates the status of a review.

    This function allows administrators to approve or reject a review based on its content.
    It accepts a POST request to change the review's status to either 'Approved' or 'Rejected'.

    Arguments:
        review_id (int): The ID of the review to be moderated.

    Request Data:
        JSON containing the status to set ('Approved' or 'Rejected').

    Returns:
        JSON response with success or error message:
            - Success: {"message": "Review status updated to <status>"}, status code 200
            - Failure: {"message": "Review not found"} or {"message": "Invalid status"}, status code 404 or 400
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json()
    if data['status'] not in ['Approved', 'Rejected']:
        return jsonify({"message": "Invalid status"}), 400

    review.status = data['status']
    db.session.commit()
    return jsonify({"message": f"Review status updated to {review.status}"})


if __name__ == '__main__':
    """
    Runs the Flask application.

    Starts the Flask web server on host 0.0.0.0 and port 5004 in debug mode.

    Arguments:
        None
    
    Returns:
        None
    """
    app.run(debug=True, host='0.0.0.0', port=5004)
