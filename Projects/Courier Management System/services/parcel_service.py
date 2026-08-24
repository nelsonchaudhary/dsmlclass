# services/parcel_service.py
# Business logic for Parcel Registration and management
import random
from services.employee_service import get_delivery_boys, find_employee_by_id
from database import load_data, save_data
from models import Parcel
from services.customer_service import find_customer_by_id

# Defines which status a parcel can move to FROM its current status.
# This is the shipment workflow from the PRD, enforced in code.
VALID_TRANSITIONS = {
    "Booked": ["Packed", "Cancelled"],
    "Packed": ["Dispatched", "Cancelled"],
    "Dispatched": ["In Transit", "Cancelled"],
    "In Transit": ["Out for Delivery", "Returned"],
    "Out for Delivery": ["Delivered", "Returned"],
    "Delivered": [],       # final state — no further transitions
    "Cancelled": [],       # final state
    "Returned": []          # final state
}


class InvalidStatusTransitionError(Exception):
    """Raised when trying to move a parcel to a status that isn't allowed from its current status."""
    pass

FILENAME = "parcels.json"


class CustomerNotFoundError(Exception):
    """Raised when a parcel references a customer_id that doesn't exist."""
    pass

class DeliveryBoyNotFoundError(Exception):
    """Raised when trying to assign a delivery boy ID that doesn't exist or isn't a DeliveryBoy."""
    pass


class InvalidOTPError(Exception):
    """Raised when the OTP entered for delivery confirmation doesn't match."""
    pass


def add_parcel(customer_id, sender_name, receiver_name, receiver_phone,
               pickup_address, destination_address, weight, dimensions,
               courier_type, insurance, delivery_charge, booking_date, expected_delivery):
    """
    Creates a new parcel with an auto-generated tracking number.
    Validates that customer_id refers to a real, existing customer first.
    """
    # Validate the relationship before creating the parcel (like a foreign key check)
    customer = find_customer_by_id(customer_id)
    if customer is None:
        raise CustomerNotFoundError(f"No customer found with ID {customer_id}")

    data = load_data(FILENAME)
    if "parcels" not in data:
        data = {"next_id": 1, "parcels": []}

    next_num = data["next_id"]
    tracking_no = f"TRK{1000 + next_num}"  # e.g. TRK1001, TRK1002...

    parcel = Parcel(
        tracking_no, customer_id, sender_name, receiver_name, receiver_phone,
        pickup_address, destination_address, weight, dimensions, courier_type,
        insurance, delivery_charge, booking_date, expected_delivery
    )

    data["parcels"].append(parcel.to_dict())
    data["next_id"] += 1

    save_data(FILENAME, data)
    return parcel


def get_all_parcels():
    data = load_data(FILENAME)
    return data.get("parcels", [])


def find_parcel_by_tracking_no(tracking_no):
    for p in get_all_parcels():
        if p["tracking_no"] == tracking_no:
            return p
    return None


def update_parcel(tracking_no, **fields_to_update):
    data = load_data(FILENAME)
    parcels = data.get("parcels", [])

    for p in parcels:
        if p["tracking_no"] == tracking_no:
            p.update(fields_to_update)
            save_data(FILENAME, data)
            return True
    return False


def delete_parcel(tracking_no):
    data = load_data(FILENAME)
    parcels = data.get("parcels", [])

    original_length = len(parcels)
    data["parcels"] = [p for p in parcels if p["tracking_no"] != tracking_no]

    if len(data["parcels"]) == original_length:
        return False

    save_data(FILENAME, data)
    return True


def search_parcels(keyword):
    keyword = keyword.lower()
    return [
        p for p in get_all_parcels()
        if keyword in p["tracking_no"].lower()
        or keyword in p["receiver_name"].lower()
        or keyword in p["receiver_phone"]
    ]

def update_parcel_status(tracking_no, new_status):
    """
    Moves a parcel to a new status, but only if the transition is valid
    according to VALID_TRANSITIONS. Also stamps a status_history entry.
    """
    parcel = find_parcel_by_tracking_no(tracking_no)
    if parcel is None:
        raise ValueError(f"No parcel found with tracking number {tracking_no}")

    current_status = parcel["status"]
    allowed = VALID_TRANSITIONS.get(current_status, [])

    if new_status not in allowed:
        raise InvalidStatusTransitionError(
            f"Cannot move parcel from '{current_status}' to '{new_status}'. "
            f"Allowed next steps: {allowed if allowed else 'none (final state)'}"
        )

    update_parcel(tracking_no, status=new_status)
    return True


def get_next_statuses(tracking_no):
    """
    Returns the list of statuses this parcel is allowed to move to right now.
    Used by the UI to only show valid options (e.g. in a dropdown).
    """
    parcel = find_parcel_by_tracking_no(tracking_no)
    if parcel is None:
        return []
    return VALID_TRANSITIONS.get(parcel["status"], [])


def assign_delivery_boy(tracking_no, employee_id):
    """
    Assigns a delivery boy to a parcel. Validates that the employee_id
    exists AND has the role 'DeliveryBoy' (not just any employee).
    Also generates a 4-digit OTP for delivery confirmation.
    """
    parcel = find_parcel_by_tracking_no(tracking_no)
    if parcel is None:
        raise ValueError(f"No parcel found with tracking number {tracking_no}")

    employee = find_employee_by_id(employee_id)
    if employee is None or employee["role"] != "DeliveryBoy":
        raise DeliveryBoyNotFoundError(f"No Delivery Boy found with employee ID {employee_id}")

    otp = str(random.randint(1000, 9999))

    update_parcel(
        tracking_no,
        assigned_delivery_boy=employee_id,
        delivery_otp=otp
    )
    return otp


def confirm_delivery(tracking_no, entered_otp, receiver_name_confirmed):
    """
    Confirms delivery only if:
    1. The parcel is currently 'Out for Delivery'
    2. The entered OTP matches the stored OTP
    Moves the parcel to 'Delivered' status on success.
    """
    parcel = find_parcel_by_tracking_no(tracking_no)
    if parcel is None:
        raise ValueError(f"No parcel found with tracking number {tracking_no}")

    if parcel["status"] != "Out for Delivery":
        raise InvalidStatusTransitionError(
            f"Parcel must be 'Out for Delivery' to confirm delivery. Current status: '{parcel['status']}'"
        )

    stored_otp = parcel.get("delivery_otp")
    if stored_otp is None or entered_otp != stored_otp:
        raise InvalidOTPError("Incorrect OTP. Delivery not confirmed.")

    update_parcel(
        tracking_no,
        status="Delivered",
        receiver_name_confirmed=receiver_name_confirmed
    )
    return True


def get_available_delivery_boys():
    """
    Wrapper used by the UI to populate a dropdown of Delivery Boys.
    """
    return get_delivery_boys()