import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
from flask import Flask, request, jsonify
from database.models import db, Review, Customer, Inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Performance profiling: Start profiling before each request
@app.before_request
def start_profiling():
    request.profiler = cProfile.Profile()
    request.profiler.enable()

# Performance profiling: Stop profiling and log results after each request
@app.after_request
def stop_profiling(response):
    if hasattr(request, 'profiler'):
        request.profiler.disable()
        s = StringIO()
        ps = pstats.Stats(request.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Log top 10 slowest functions
        app.logger.info(s.getvalue())
    return response

# Memory profiling example: Annotate critical function
@profile
@app.route('/reviews/submit', methods=['POST'])
def submit_review():
    """
    Submits a new review for a product by a customer.
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

@app.route('/reviews/update/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Updates an existing review.
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

@app.route('/reviews/delete/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Deletes a review from the database.
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"})

@app.route('/reviews/product/<int:item_id>', methods=['GET'])
def get_product_reviews(item_id):
    """
    Retrieves all reviews for a specific product.
    """
    reviews = Review.query.filter_by(inventory_id=item_id).all()
    if not reviews:
        return jsonify({"message": "No reviews found for this product"}), 404

    reviews_list = [
        {"id": review.id, "customer_id": review.customer_id, "rating": review.rating, "comment": review.comment, "status": review.status}
        for review in reviews
    ]
    return jsonify(reviews_list)

@app.route('/reviews/moderate/<int:review_id>', methods=['POST'])
def moderate_review(review_id):
    """
    Moderates the status of a review.
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
    app.run(debug=True, host='0.0.0.0', port=5004)
