import re

import pymongo
"""
    Online store, with 3 collections: products, customers, orders
    products have: _id, product_id, name, price, stock, category 
    customers have: _id, customer_id, name, email, phone, address 
    orders have: _id, order_id, customer_id, items
"""
def connect(host, port, timeout):
    try:
        client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=timeout)
        client.server_info()
        return client
    except Exception as e:
        print(f"Error: {e}")
        return None


def create_database(client):
    db = client["online_store"]
    products_collection = db["products"]
    customers_collection = db["customers"]
    orders_collection = db["orders"]
    return db, products_collection, customers_collection, orders_collection


def add_product(products_collection, product_id, name, price, stock, category):
    # Prevent duplicates
    if products_collection.find_one({"product_id": product_id}):
        print(f"Error: product_id {product_id} already exists!")
        return None
    # Expected types
    fields = {"product_id" : str,
              "name" : str,
              "price" : (int, float),
              "stock" : int,
              "category" : str}
    # Actual values
    values = {"product_id": product_id,
              "name": name,
              "price": price,
              "stock": stock,
              "category": category}
    # Validate types
    for field_name, expected_type in fields.items():
        value = values[field_name]
        if not isinstance(value, expected_type):
            print(f"Field {field_name} should be of type {expected_type}")
            return None

    # Check if not empty
    for field_name, value in values.items():
        if isinstance(value, float) == True or isinstance(value, int) == True:
            continue
        value = value.strip()
        if len(value) < 1:
            print(f"{field_name.title()} must be at least 1 character!")
            return None

    print(f"Added product with id {product_id}")
    return products_collection.insert_one(values)


def update_product(products_collection, product_id, **updates):
    # Check if product exists
    if not products_collection.find_one({"product_id": product_id}):
        print(f"Error: no product with product_id {product_id}!")
        return None
    # Expected types
    fields = {"name": str,
              "price": (int, float),
              "stock": int,
              "category": str}
    # Check for invalid fields
    for field_name, value in updates.items():
        if field_name not in fields:
            print(f"Field {field_name} is not a valid field for update.")
            return None
        # Ensure expected_type is a tuple for isinstance()
        expected_type = fields[field_name]
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        # Type check
        if not isinstance(value, expected_type): # noqa
            print(f"Error: wrong data type in update_product {updates}")
            return None

    # Check if not empty
    for value in updates.values():
        if not isinstance(value, str):
            continue
        value = value.strip()
        if len(value) < 1:
            print(f"Update value must be at least 1 character!")
            return None

    # Update
    result = products_collection.update_one({"product_id" : product_id}, {"$set" : updates})
    # If changes made and otherwise
    if result.modified_count:
        print(f"Updated product {product_id} with updates: {updates}")
    else:
        print(f"No changes made to {product_id}")
    return result


def add_customer(customers_collection, customer_id, name, email, phone, address):
    """
        Purpose: Add a new customer after checking that customer_id is unique, email is valid,
         phone number is valid and all field types are valid
        Customer fields to validate:
            "customer_id" : str
            "name" : str
            "email" : str
            "phone" : str
            "address" : str
        Return: InsertOneResult if successful, else None
    """
    # Prevent duplicates
    if customers_collection.find_one({"customer_id": customer_id}):
        print(f"Customer id must be unique!")
        return None

    # Validate fields
    # Expected types
    fields = {"customer_id": str,
              "name": str,
              "email": str,
              "phone": str,
              "address": str}
    # Actual values
    values = {"customer_id": customer_id,
              "name": name,
              "email": email,
              "phone": phone,
              "address": address}
    for field_name, expected_type in fields.items():
        value = values[field_name]
        if not isinstance(value, expected_type):
            print(f"Field {field_name} should be of type {expected_type}")
            return None

    # Check if not empty
    for field_name, value in values.items():
        value = value.strip()
        if len(value) < 1:
            print(f"{field_name.title()} must be at least 1 character!")
            return None

    # Validate email address
    if email.find("@") == -1:
        print(f"Invalid email: {email}, must include @")
        return None
    email_test = email.split("@")
    if not email_test[0]:
        print(f"Invalid email: {email}, username can't be empty or start with @")
        return None
    if not email_test[1]:
        print(f"Invalid email: {email}, domain can't be empty")
        return None
    email_test = email_test[1]
    if email_test.find(".") == -1:
        print(f"Invalid email: {email}, domain must include .")
        return None
    email_test = email_test.split(".")
    if not email_test[0]:
        print(f"Invalid email: {email}, left side of domain cant't be empty")
        return None
    if not email_test[1]:
        print(f"Invalid email: {email}, right side of domain cant't be empty")
        return None

    # Validate email using regex - I wasn't sure if that was allowed
    valid_email = re.compile(r"[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z0-9]+")
    valid_email.match(email)
    #if not valid_email.match(email):
    #    print(f"Invalid email: {email}, wrong format")
    #    return None


    # Validate phone number
    phone_test = list(phone)
    numbers = 0
    for val in phone_test:
        if val.isdigit():
            numbers += 1
        else:
            if val == "-" or val == "(" or val == ")" or val == " ":
                continue
            else:
                print(f"Invalid phone number: {phone}, can't include {val}")
                return None
    if numbers < 7:
        print(f"Invalid phone number: {phone}, can't be less than 7 digits")
        return None


    new_customer = values
    result = customers_collection.insert_one(new_customer)
    print(f"Added customer: {new_customer}")
    return result


def update_customer(customers_collection, customer_id, **updates):
    """
        Purpose: Update one or more fields of an existing customer after validating allowed fields and types
        Notes: Fields that can be updated: name, email, phone, address
        Return: UpdateResult if successful, else None
    """
    # Check if product exists
    if not customers_collection.find_one({"customer_id": customer_id}):
        print(f"Error: no customer with customer_id {customer_id}!")
        return None
    # Expected types
    fields = {
              "name": str,
              "email": str,
              "phone": str,
              "address": str}

    # Check for invalid fields
    for field_name, value in updates.items():
        if field_name not in fields:
            print(f"Field {field_name} is not a valid field for update.")
            return None
        # Ensure expected_type is a tuple for isinstance()
        expected_type = fields[field_name]
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        # Type check
        if not isinstance(value, expected_type): # noqa
            print(f"Error: wrong data type in update_customer {updates}")
            return None

    # Check if not empty
    for  value in updates.values():
        value = value.strip()
        if len(value) < 1:
            print(f"Update value must be at least 1 character!")
            return None

    if 'email' in updates.keys():
        email = updates['email']
        # Validate email address
        if email.find("@") == -1:
            print(f"Invalid email: {email}, must include @")
            return None
        email_test = email.split("@")
        if not email_test[0]:
            print(f"Invalid email: {email}, username can't be empty or start with @")
            return None
        if not email_test[1]:
            print(f"Invalid email: {email}, domain can't be empty")
            return None
        email_test = email_test[1]
        if email_test.find(".") == -1:
            print(f"Invalid email: {email}, domain must include .")
            return None
        email_test = email_test.split(".")
        if not email_test[0]:
            print(f"Invalid email: {email}, left side of domain cant't be empty")
            return None
        if not email_test[1]:
            print(f"Invalid email: {email}, right side of domain cant't be empty")
            return None

    if 'phone' in updates.keys():
        phone = updates['phone']
        # Validate phone number
        phone_test = list(phone)
        numbers = 0
        for val in phone_test:
            if val.isdigit():
                numbers += 1
            else:
                if val == "-" or val == "(" or val == ")" or val == " ":
                    continue
                else:
                    print(f"Invalid phone number: {phone}, can't include {val}")
                    return None
        if numbers < 7:
            print(f"Invalid phone number: {phone}, can't be less than 7 digits")
            return None

    # Update
    result = customers_collection.update_one({"customer_id": customer_id}, {"$set" : updates})
    # If changes made and otherwise
    if result.modified_count:
        print(f"Updated customer {customer_id} with updates: {updates}")
    else:
        print(f"No changes made to {customer_id}")
    return result


def add_order(orders_collection, customers_collection, products_collection, order_id, customer_id, items):
    # Check if order exists
    if orders_collection.find_one({"order_id": order_id}):
        print(f"Error: order_id {order_id} already exists!")
        return None
    # Check if customer exists
    if not customers_collection.find_one({"customer_id": customer_id}):
        print(f"Error: {customer_id} doesn't exists!")
        return None
    # Check if items are not empty
    if not isinstance(items, list) or not items:
        print(f"Error: in add-order items must be a non-empty list!")
        return None

    # Check if not empty
    for  value in [order_id, customer_id]:
        value = value.strip()
        if len(value) < 1:
            print(f"All order values must be at least 1 character!")
            return None
    for dictionary in items:
        for value in dictionary.values():
            if not isinstance(value, str):
                continue
            value = value.strip()
            if len(value) < 1:
                print(f"All values in items must be at least 1 character!")
                return None

    order_items = []
    total_price = 0.0
    # Check items
    for item in items:
        if not isinstance(item, dict):
            print(f"Error: each item must be a dictionary!")
            return None

        product_id = item.get("product_id")
        quantity = item.get("quantity")
        if not isinstance(product_id, str) or not isinstance(quantity, int):
            print(f"Error: invalid product_id or quantity type!")
            return None

        product = products_collection.find_one({"product_id": product_id})
        if not product:
            print(f"Error: product {product_id} does not exists")
            return None

        if product["stock"] < quantity:
            print(f"Error: insufficient stock for product {product_id}")
            return None

        price = float(product["price"])
        total_price += price * quantity

        order_items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
        })

        # Reduce stock
    for item in order_items:
        products_collection.update_one(
            {"product_id": item["product_id"]},
            {"$inc": {"stock": -item["quantity"]}}
        )

    order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items,
        "total_price": total_price
    }
    print(f"Added order {order_id} for customer {customer_id}")
    return orders_collection.insert_one(order)


def view_orders_by_customer(orders_collection, customer_id):
    print(f"Orders of customer with id {customer_id}:")

    orders = list(orders_collection.find({"customer_id": customer_id}, {'_id': 0}))
    if not orders:
        print(f"No orders for customer with id {customer_id}")
        return None

    for order in orders:
        print(order)

    return orders


def count_orders_per_customer(orders_collection):
    print("Number of orders per customer: ")
    pipeline = [
        {"$group": {
            "_id": "$customer_id",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}  # DESC
    ]
    for result in orders_collection.aggregate(pipeline):
        print(result["_id"], ':', result["count"])


def total_spent_per_customer(orders_collection):
    print("Total spent per customer: ")
    pipeline = [
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$total_price"}
        }},
        {"$sort": {"total_spent": -1}}
    ]
    for result in orders_collection.aggregate(pipeline):
        print(result["_id"], ':', "{number:.2f}".format(number=result["total_spent"]))


def delete_one(collection, _id):
    # Check if exists
    name = str(collection.name[0:-1])
    item = collection.find_one({name + "_id" : _id})
    if not item:
        print(f"No {name} with {name + "_id"} {_id}")
        return None
    else:
        print(f"Deleting {name} with {name + "_id"} {_id}")
        return collection.delete_one({name + "_id" : _id})


def view_one(collection, _id):
    name = str(collection.name[0:-1]) + '_id'
    item = collection.find_one({name: _id})
    if item:
        print(f"{collection.name[0:-1].title()} found {item}")
        return item
    else:
        print(f"No {collection.name} with id: {_id}")
        return None


def view_all(collection):
    print(f"All {collection.name}: ")
    items = list(collection.find())
    for item in items:
        print(f"{item}")
    return items


def main():
    client = connect("localhost", 27017, 1000)
    if client is None:
        print("Quitting...")
        return
    db, products_collection, customers_collection, orders_collection = create_database(client)
    # For reruns
    products_collection.delete_many({})
    customers_collection.delete_many({})
    orders_collection.delete_many({})

    # Valid inserts
    add_product(products_collection, "P00001", "Keyboard", 499.99, 10, "Peripherals")
    add_product(products_collection, "P00002", "Mouse", 199.99, 20, "Peripherals")
    add_product(products_collection, "P00003", "Mouse", 75, 15, "Peripherals")
    add_product(products_collection, "P00004", "Headset", 106, 15, "Peripherals")
    add_product(products_collection, "P00006", "GPU", 3500, 4, "PC components")
    add_product(products_collection, "P00008", "RAM", 1000, 0, "PC components")
    add_product(products_collection, "P00009", "CPU", 1200, 6, "PC components")
    add_product(products_collection, "P00010", "CPU", 901, 3, "PC components")

    add_customer(customers_collection, 'C01', "Anna", "anna@email.com", '123456789', "adres1")
    add_customer(customers_collection, 'C02', "Joanna", "joanna@email.com", '234567891', "adres2")
    add_customer(customers_collection, 'C03', "Zuzanna", "zuzanna@email.com", '345678912', "adres3")
    add_customer(customers_collection, 'C04', "Marianna", "marianna@email.com", '456789123', "adres3")
    add_customer(customers_collection, 'C05', "Hanna", "hanna@email.com", '567891234', "adres4")

    add_order(orders_collection, customers_collection, products_collection, "o1", "C01",
              [{"product_id": "P00001", "quantity": 2}, {"product_id": "P00003", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o2", "C01",
              [{"product_id": "P00001", "quantity": 2}, {"product_id": "P00003", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o3", "C02",
              [{"product_id": "P00002", "quantity": 1}, {"product_id": "P00003", "quantity": 2}])
    add_order(orders_collection, customers_collection, products_collection, "o4", "C03",
              [{"product_id": "P00006", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o5", "C04",
              [{"product_id": "P00009", "quantity": 1}, {"product_id": "P00010", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o6", "C01",
              [{"product_id": "P00001", "quantity": 3}])
    add_order(orders_collection, customers_collection, products_collection, "o7", "C02",
              [{"product_id": "P00003", "quantity": 1}, {"product_id": "P00010", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o8", "C03",
              [{"product_id": "P00002", "quantity": 2}, {"product_id": "P00001", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o9", "C04",
              [{"product_id": "P00006", "quantity": 1}, {"product_id": "P00003", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o10", "C01",
              [{"product_id": "P00009", "quantity": 2}])
    add_order(orders_collection, customers_collection, products_collection, "o11", "C02",
              [{"product_id": "P00001", "quantity": 1}, {"product_id": "P00002", "quantity": 1},
               {"product_id": "P00003", "quantity": 1}])
    add_order(orders_collection, customers_collection, products_collection, "o12", "C03",
              [{"product_id": "P00010", "quantity": 1}])

    #--------Zadanie 1---------

    # Test empty string with customers
    add_customer(customers_collection, 'C06', "", "marianna@email.com", '456789123', "adres3")
    #Test string with spaces
    add_customer(customers_collection, 'C06', "Hanna", "   ", '456789123', "adres3")
    #Test update_customer with empty string
    update_customer(customers_collection, 'C01', phone='')

    # Test empty string with products
    add_product(products_collection, "P00011", "", 499.99, 10, "Peripherals")
    #Test string with spaces
    add_product(products_collection, "P00011", "Mouse", 99.99, 3, "   ")
    #Test update_product with empty string
    update_product(products_collection, 'P00010', name='  ')

    # Test empty string with orders
    add_order(orders_collection, customers_collection, products_collection, "o13", "C03",
              [{"product_id": "", "quantity": 1}])
    # Test string with spaces
    add_order(orders_collection, customers_collection, products_collection, "  ", "C03",
              [{"product_id": "P00011", "quantity": 1}])

    # Customer with orders
    view_orders_by_customer(orders_collection, 'C01')
    # Customer with no orders
    view_orders_by_customer(orders_collection, 'C05')


    #--------Zadanie 2---------
    # Walidacja adresu email- brak '@'
    add_customer(customers_collection, 'C06', "Marzanna", "marzannaemail.com", '567891234', "adres5")
    # Brak '.'
    add_customer(customers_collection, 'C06', "Marzanna", "marzanna@emailcom", '567891234', "adres5")
    # Pusty username
    add_customer(customers_collection, 'C06', "Marzanna", "@email.com", '567891234', "adres5")
    # Pusta prawa część domeny
    add_customer(customers_collection, 'C06', "Marzanna", "marzanna@.com", '567891234', "adres5")
    # Pusta lewa część domeny
    add_customer(customers_collection, 'C06', "Marzanna", "marzanna@email.", '567891234', "adres5")
    # Walidacja w update
    update_customer(customers_collection, 'C01', email='@email.com')

    # Walidacja numeru telefonu- poprawny, zawiera '-', ' ', '(', ')'
    add_customer(customers_collection, 'C06', "Marzanna", "marzanna@email.com", '56 7891-234)(', "adres5")
    # Niepoprawny, zawiera '/'
    add_customer(customers_collection, 'C07', "Lilianna", "lilianna@email.com", '6789/12345', "adres5")
    # Niepoprawny, zawiera niż 7 cyfr
    add_customer(customers_collection, 'C07', "Lilianna", "lilianna@email.com", '123456', "adres5")
    # Walidacja w update
    update_customer(customers_collection, 'C01', phone='123a456')


    #--------Zadanie 3---------
    count_orders_per_customer(orders_collection)
    total_spent_per_customer(orders_collection)


    view_one(customers_collection, 'C01')
    view_one(products_collection, 'P00010')
    delete_one(orders_collection, 'o11')

    # Close the client at the end
    client.close()


if __name__ == '__main__':
    main()
