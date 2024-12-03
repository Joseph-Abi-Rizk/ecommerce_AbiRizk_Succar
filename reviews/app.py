from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import cProfile
import pstats
from io import StringIO
from memory_profiler import profile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/pc/OneDrive/Desktop/uni/FALL 25/eece435L/ecommerce_AbiRizk_Succar/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'YourSecretKey'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models: Review, Customer, Inventory

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

@profile
@app.route('/reviews/submit', methods=['POST'])
@jwt_required()
def submit_review():
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
    return jsonify({"message": "Review updated successfully"}), 200

@app.route('/reviews/delete/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404

    db.session.delete(review)
    db.session.commit()
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
    return jsonify({"message": f"Review status updated to {review.status}"}), 200
