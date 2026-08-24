# services/employee_service.py
# Business logic for Employee & Delivery Boy Management

from database import load_data, save_data
from models import Employee, DeliveryBoy, Admin

FILENAME = "employees.json"


def add_employee(name, phone, email, address, department, salary, designation, joining_date, role="Operator"):
    """
    Creates a new employee record. role should be "Admin", "Operator", or "DeliveryBoy".
    Uses the matching OOP class based on role (polymorphism in action).
    """
    data = load_data(FILENAME)
    if "employees" not in data:
        data = {"next_id": 1, "employees": []}

    new_id = data["next_id"]

    if role == "DeliveryBoy":
        employee = DeliveryBoy(new_id, name, phone, email, address, department, salary, designation, joining_date)
    elif role == "Admin":
        employee = Admin(new_id, name, phone, email, address, department, salary, designation, joining_date)
    else:
        employee = Employee(new_id, name, phone, email, address, department, salary, designation, joining_date)

    data["employees"].append(employee.to_dict(role=role))
    data["next_id"] += 1

    save_data(FILENAME, data)
    return employee


def get_all_employees():
    data = load_data(FILENAME)
    return data.get("employees", [])


def get_delivery_boys():
    """
    Returns only employees with role 'DeliveryBoy'.
    Used later when assigning a delivery boy to a parcel.
    """
    return [e for e in get_all_employees() if e["role"] == "DeliveryBoy"]


def find_employee_by_id(employee_id):
    for emp in get_all_employees():
        if emp["employee_id"] == employee_id:
            return emp
    return None


def update_employee(employee_id, **fields_to_update):
    data = load_data(FILENAME)
    employees = data.get("employees", [])

    for emp in employees:
        if emp["employee_id"] == employee_id:
            emp.update(fields_to_update)
            save_data(FILENAME, data)
            return True
    return False


def delete_employee(employee_id):
    data = load_data(FILENAME)
    employees = data.get("employees", [])

    original_length = len(employees)
    data["employees"] = [e for e in employees if e["employee_id"] != employee_id]

    if len(data["employees"]) == original_length:
        return False

    save_data(FILENAME, data)
    return True


def search_employees(keyword):
    keyword = keyword.lower()
    return [
        e for e in get_all_employees()
        if keyword in e["name"].lower()
        or keyword in e["phone"]
        or keyword in e["designation"].lower()
    ]