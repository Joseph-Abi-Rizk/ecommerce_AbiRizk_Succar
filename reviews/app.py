from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import cProfile
import pstats
from io import StringIO
from memory_profiler import profile
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_caching import Cache

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
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

# Sentry setup
sentry_sdk.init(
    dsn="https://<your_sentry_dsn>",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0  # Track every transaction
)

# Models: Review, Customer, Inventory
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    count = db.Column(db.Integer, nullable=False)

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

# Health Check
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if the database is up
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "failed"}), 500

# Routes
@profile
@app.route('/reviews/submit', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submits a new review for a product by a customer.
    """
    data = request.get_json()
    customer = Customer.query.filter_by(username=data['username']).first()
    item = Inventory.query.get(data['item_id'])

    if not customer or not item:
        return jsonify({"message": "Customer or item not found"}), 404

    # Validate rating
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
    """
    Updates an existing review.
    """
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
    """
    Deletes a review.
    """
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
    """
    Moderates the status of a review (Approved/Rejected).
    """
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

# Error Handling with Sentry
@app.route('/error')
def error_route():
    """
    Test route for error logging to Sentry.
    """
    try:
        # Simulate an error
        1 / 0
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return jsonify({"message": "Error logged to Sentry"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
