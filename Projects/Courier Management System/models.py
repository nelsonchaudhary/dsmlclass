# models.py
# Defines the core OOP classes used across the system.

class Person:
    """
    Base class representing any person in the system.
    Customer, Employee, Admin, and DeliveryBoy all inherit from this.
    """

    def __init__(self, name, phone, email, address):
        # Encapsulation: attributes prefixed with _ are "protected"
        # (a convention in Python, not enforced like other languages)
        self._name = name
        self._phone = phone
        self._email = email
        self._address = address

    # Getter methods control how outside code reads the data
    def get_name(self):
        return self._name

    def get_phone(self):
        return self._phone

    def get_email(self):
        return self._email

    def get_address(self):
        return self._address

    def get_details(self):
        """
        Base method — subclasses will override (polymorphism) this
        to show role-specific details.
        """
        return f"Name: {self._name}, Phone: {self._phone}, Email: {self._email}"


class Customer(Person):
    """
    Represents a customer who books parcels.
    Inherits shared fields (name, phone, email, address) from Person.
    """

    def __init__(self, customer_id, name, phone, email, address, city, postal_code, created_date):
        super().__init__(name, phone, email, address)
        self._customer_id = customer_id
        self._city = city
        self._postal_code = postal_code
        self._created_date = created_date

    def get_customer_id(self):
        return self._customer_id

    def get_details(self):
        # Polymorphism: overrides Person's get_details() with customer-specific info
        base = super().get_details()
        return f"{base}, City: {self._city}, Postal Code: {self._postal_code}"

    def to_dict(self):
        """
        Converts this object into a dictionary so it can be saved as JSON.
        """
        return {
            "customer_id": self._customer_id,
            "name": self._name,
            "phone": self._phone,
            "email": self._email,
            "address": self._address,
            "city": self._city,
            "postal_code": self._postal_code,
            "created_date": self._created_date
        }


class Employee(Person):
    """
    Represents a staff member. Admin and DeliveryBoy inherit from this.
    """

    def __init__(self, employee_id, name, phone, email, address, department, salary, designation, joining_date):
        super().__init__(name, phone, email, address)
        self._employee_id = employee_id
        self._department = department
        self._salary = salary
        self._designation = designation
        self._joining_date = joining_date

    def get_employee_id(self):
        return self._employee_id

    def get_details(self):
        base = super().get_details()
        return f"{base}, Designation: {self._designation}, Department: {self._department}"

    def to_dict(self, role="Employee"):
        """
        Converts this object into a dictionary so it can be saved as JSON.
        role is passed in since Employee, Admin, and DeliveryBoy all use this.
        """
        return {
            "employee_id": self._employee_id,
            "name": self._name,
            "phone": self._phone,
            "email": self._email,
            "address": self._address,
            "department": self._department,
            "salary": self._salary,
            "designation": self._designation,
            "joining_date": self._joining_date,
            "role": role
        }
    


class DeliveryBoy(Employee):
    """
    A specialized Employee who delivers parcels.
    """

    def __init__(self, employee_id, name, phone, email, address, department, salary, designation, joining_date):
        super().__init__(employee_id, name, phone, email, address, department, salary, designation, joining_date)
        self._assigned_parcels = []  # tracking numbers currently assigned

    def assign_parcel(self, tracking_no):
        self._assigned_parcels.append(tracking_no)

    def get_details(self):
        base = super().get_details()
        return f"{base}, Assigned Parcels: {len(self._assigned_parcels)}"


class Admin(Employee):
    """
    A specialized Employee with system management privileges.
    """

    def get_details(self):
        base = super().get_details()
        return f"{base}, Role: Admin"


class Parcel:
    """
    Represents a parcel/courier booking.
    Not a Person, so it doesn't inherit from Person — it's a standalone entity
    that references a Customer by ID.
    """

    def __init__(self, tracking_no, customer_id, sender_name, receiver_name, receiver_phone,
                 pickup_address, destination_address, weight, dimensions, courier_type,
                 insurance, delivery_charge, booking_date, expected_delivery,
                 status="Booked", assigned_delivery_boy=None):
        self._tracking_no = tracking_no
        self._customer_id = customer_id
        self._sender_name = sender_name
        self._receiver_name = receiver_name
        self._receiver_phone = receiver_phone
        self._pickup_address = pickup_address
        self._destination_address = destination_address
        self._weight = weight
        self._dimensions = dimensions
        self._courier_type = courier_type
        self._insurance = insurance
        self._delivery_charge = delivery_charge
        self._booking_date = booking_date
        self._expected_delivery = expected_delivery
        self._status = status
        self._assigned_delivery_boy = assigned_delivery_boy

    def get_tracking_no(self):
        return self._tracking_no

    def get_status(self):
        return self._status

    def to_dict(self):
        return {
            "tracking_no": self._tracking_no,
            "customer_id": self._customer_id,
            "sender_name": self._sender_name,
            "receiver_name": self._receiver_name,
            "receiver_phone": self._receiver_phone,
            "pickup_address": self._pickup_address,
            "destination_address": self._destination_address,
            "weight": self._weight,
            "dimensions": self._dimensions,
            "courier_type": self._courier_type,
            "insurance": self._insurance,
            "delivery_charge": self._delivery_charge,
            "booking_date": self._booking_date,
            "expected_delivery": self._expected_delivery,
            "status": self._status,
            "assigned_delivery_boy": self._assigned_delivery_boy
        }


class Payment:
    """
    Represents a payment made against a parcel.
    References a parcel by tracking_no, not by direct object reference —
    same pattern as Parcel referencing Customer by customer_id.
    """

    VAT_RATE = 0.13  # 13% VAT

    def __init__(self, payment_id, tracking_no, amount, method, status, payment_date):
        self._payment_id = payment_id
        self._tracking_no = tracking_no
        self._amount = amount
        self._vat = round(amount * self.VAT_RATE, 2)
        self._total = round(amount + self._vat, 2)
        self._method = method
        self._status = status
        self._payment_date = payment_date

    def get_total(self):
        return self._total

    def to_dict(self):
        return {
            "payment_id": self._payment_id,
            "tracking_no": self._tracking_no,
            "amount": self._amount,
            "vat": self._vat,
            "total": self._total,
            "method": self._method,
            "status": self._status,
            "payment_date": self._payment_date
        }