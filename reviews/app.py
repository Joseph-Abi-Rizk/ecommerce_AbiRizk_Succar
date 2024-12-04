from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
import logging
from flask_caching import Cache

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\nsucc\\Desktop\\python env\\ecommerce_AbiRizk_Succar\\database\\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YourSecretKey'
app.config['CACHE_TYPE'] = 'simple'  # You can change this to 'redis' for better performance
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cache = Cache(app)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Outputs logs to console
        logging.FileHandler('reviews_app.log')  # Logs saved to reviews_app.log
    ]
)

logger = logging.getLogger(__name__)

# Models
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    wallet_balance = db.Column(db.Float)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    count = db.Column(db.Integer, nullable=False)

# Performance profiling
@app.before_request
def start_profiling():
    request.profiler = cProfile.Profile()
    request.profiler.enable()

@app.after_request
def stop_profiling(response):
    if hasattr(request, 'profiler'):
        request.profiler.disable()
        s = StringIO()
        ps = pstats.Stats(request.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        app.logger.info(s.getvalue())
    return response

# Routes
@profile
@app.route('/reviews/submit', methods=['POST'])
@jwt_required()
def submit_review():
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    item = Inventory.query.get(data['item_id'])

    if not customer or not item:
        return jsonify({"message": "Customer or item not found"}), 404

    if not 1 <= data['rating'] <= 5:
        return jsonify({"message": "Rating must be between 1 and 5"}), 400

    new_review = Review(
        customer_id=customer.id,
        inventory_id=item.id,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    db.session.add(new_review)
    db.session.commit()
    logger.info(f"Review submitted: {data['username']} for {item.name}")
    return jsonify({"message": "Review submitted successfully"}), 201

@app.route('/reviews/update/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json()
    if 'rating' in data and not 1 <= data['rating'] <= 5:
        return jsonify({"message": "Rating must be between 1 and 5"}), 400
    if 'rating' in data:
        review.rating = data['rating']
    if 'comment' in data:
        review.comment = data['comment']

    db.session.commit()
    logger.info(f"Review updated: {review.id}")
    return jsonify({"message": "Review updated successfully"}), 200

@app.route('/reviews/delete/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    db.session.delete(review)
    db.session.commit()
    logger.info(f"Review deleted: {review.id}")
    return jsonify({"message": "Review deleted successfully"}), 200

@app.route('/reviews/moderate/<int:review_id>', methods=['POST'])
@jwt_required()
def moderate_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    data = request.get_json()
    if data['status'] not in ['Approved', 'Rejected']:
        return jsonify({"message": "Invalid status"}), 400

    review.status = data['status']
    db.session.commit()
    logger.info(f"Review moderated: {review.id} | Status: {review.status}")
    return jsonify({"message": f"Review status updated to {review.status}"}), 200

@app.route('/reviews/product/<int:inventory_id>', methods=['GET'])
def get_product_reviews(inventory_id):
    """
    Retrieves all reviews for a specific product.
    """
    reviews = Review.query.filter_by(inventory_id=inventory_id).all()
    if not reviews:
        return jsonify({"message": "No reviews found for this product"}), 404

    reviews_list = [
        {
            "id": review.id,
            "customer_id": review.customer_id,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status
        } for review in reviews
    ]
    return jsonify(reviews_list), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
