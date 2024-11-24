Postman Collections
===================

This section contains the Postman collections for testing the APIs in the project.

Customers Service API
---------------------
**Description**: This collection tests all endpoints related to customer management.

Endpoints:
- `POST /customers/register`: Register a new customer.
- `GET /customers`: Retrieve all customers.
- `GET /customers/<username>`: Retrieve a customer by username.
- `PUT /customers/<username>`: Update customer details.
- `DELETE /customers/<username>`: Delete a customer.

**Download**: :download:`customers.json <../postman_collections/customers.json>`

Inventory Service API
---------------------
**Description**: This collection tests all endpoints related to inventory management.

Endpoints:
- `POST /inventory/add`: Add goods to inventory.
- `PUT /inventory/update/<item_id>`: Update goods in inventory.
- `POST /inventory/deduct/<item_id>`: Deduct inventory stock.
- `GET /inventory`: Retrieve all inventory items.

**Download**: :download:`inventory.json <../postman_collections/inventory.json>`

Reviews Service API
-------------------
**Description**: This collection tests all endpoints related to product reviews.

Endpoints:
- `POST /reviews/submit`: Submit a new review.
- `PUT /reviews/update/<review_id>`: Update a review.
- `DELETE /reviews/delete/<review_id>`: Delete a review.
- `GET /reviews/product/<item_id>`: Retrieve reviews for a product.
- `POST /reviews/moderate/<review_id>`: Moderate a review.

**Download**: :download:`reviews.json <../postman_collections/reviews.json>`

Sales Service API
-----------------
**Description**: This collection tests all endpoints related to sales operations.

Endpoints:
- `GET /sales/goods`: Display available goods.
- `GET /sales/goods/<item_id>`: Retrieve details of a specific good.
- `POST /sales`: Process a sale.
- `GET /sales/history/<username>`: Retrieve the purchase history of a customer.

**Download**: :download:`sales.json <../postman_collections/sales.json>`
