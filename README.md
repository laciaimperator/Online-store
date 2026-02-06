# Online-store
This project is a Python-based management system for an online store using MongoDB as the backend. It demonstrates core NoSQL database operations (CRUD), complex data validation, and analytical data processing using the MongoDB Aggregation Framework

### Key Features
Data Validation:
* Automatically rejects empty strings or strings containing only whitespace for all text fields (name, email, etc.).
* Email Validation: Custom logic ensures emails follow the user@domain.ext format with non-empty parts and a valid domain structure.
* Phone Number Validation: Verifies that phone numbers contain at least 7 digits and only allow specific formatting characters like spaces, dashes, and parentheses.

Inventory & Order Management:
* Atomic Stock Checks: Validates product availability before finalizing orders.
* Stock Synchronization: Automatically decrements product stock upon successful order placement.

Aggregation:
* Function that calculates and lists the number of orders placed by each customer.
* Function that aggregate the total spent per customer.
* Function to retrieve and display all order history for specific users.
