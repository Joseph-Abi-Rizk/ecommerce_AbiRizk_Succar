Introduction
============

Welcome to the documentation for the Ecommerce_AbiRizk_Succar project! This project provides a comprehensive solution for managing customers, inventory, sales, and product reviews in an eCommerce environment.

Project Overview
----------------
The Ecommerce_AbiRizk_Succar project is a modular application built using Flask. It is designed to manage:
- **Customers**: Handles user registration, wallet management, and customer details.
- **Inventory**: Manages goods, including their stock levels, pricing, and categories.
- **Sales**: Processes purchases, deducts stock, and maintains a sales history.
- **Reviews**: Enables customers to submit feedback and ratings for products, with moderation capabilities.

Core Components
---------------
The project consists of four main services:
1. **Customers Service**:
   - Manages customer registration, updates, and wallet transactions.
2. **Inventory Service**:
   - Handles stock levels, goods updates, and stock deduction.
3. **Sales Service**:
   - Processes sales transactions, deducts inventory, and tracks purchase history.
4. **Reviews Service**:
   - Manages customer reviews, ratings, and review moderation.

Tech Stack
----------
The project leverages the following technologies:
- **Flask**: For building RESTful APIs.
- **SQLAlchemy**: For database interactions and ORM.
- **SQLite**: For the centralized database.
- **Postman**: For API testing.
- **Sphinx**: For generating project documentation.

How It Works
------------
The project is designed as a set of modular services:
1. Each service exposes its own APIs for performing specific operations.
2. All services share a centralized database, ensuring data consistency.
3. Postman collections are provided for testing all API endpoints.

Setup
-----
To set up the project, refer to the [Setup Section](setup.rst). In summary:
- Clone the repository.
- Initialize the database.
- Run the individual Flask apps for each service.

