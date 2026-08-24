# services/customer_service.py
# Business logic for Customer Management: Add, Update, Delete, Search, View

from database import load_data, save_data
from models import Customer

FILENAME = "customers.json"


def add_customer(name, phone, email, address, city, postal_code, created_date):
    """
    Creates a new customer, assigns the next available ID,
    saves it to customers.json, and returns the created Customer object.
    """
    data = load_data(FILENAME)

    # Guard against a freshly-missing file (load_data returns {} on error)
    if "customers" not in data:
        data = {"next_id": 1, "customers": []}

    new_id = data["next_id"]

    customer = Customer(new_id, name, phone, email, address, city, postal_code, created_date)

    data["customers"].append(customer.to_dict())
    data["next_id"] += 1  # reserve the next ID for the next customer

    save_data(FILENAME, data)
    return customer


def get_all_customers():
    """
    Returns the raw list of customer dictionaries from storage.
    """
    data = load_data(FILENAME)
    return data.get("customers", [])


def find_customer_by_id(customer_id):
    """
    Returns a single customer dictionary matching the given ID, or None.
    """
    customers = get_all_customers()
    for cust in customers:
        if cust["customer_id"] == customer_id:
            return cust
    return None


def update_customer(customer_id, **fields_to_update):
    """
    Updates one or more fields of an existing customer.
    Usage: update_customer(1, phone="9811111111", city="Lalitpur")
    Returns True if updated, False if customer not found.
    """
    data = load_data(FILENAME)
    customers = data.get("customers", [])

    for cust in customers:
        if cust["customer_id"] == customer_id:
            cust.update(fields_to_update)
            save_data(FILENAME, data)
            return True

    return False  # customer not found


def delete_customer(customer_id):
    """
    Removes a customer by ID. Returns True if deleted, False if not found.
    """
    data = load_data(FILENAME)
    customers = data.get("customers", [])

    original_length = len(customers)
    data["customers"] = [c for c in customers if c["customer_id"] != customer_id]

    if len(data["customers"]) == original_length:
        return False  # nothing was removed, ID didn't exist

    save_data(FILENAME, data)
    return True


def search_customers(keyword):
    """
    Searches customers by name, phone, or email (case-insensitive, partial match).
    Returns a list of matching customer dictionaries.
    """
    keyword = keyword.lower()
    customers = get_all_customers()

    results = [
        c for c in customers
        if keyword in c["name"].lower()
        or keyword in c["phone"]
        or keyword in c["email"].lower()
    ]
    return results