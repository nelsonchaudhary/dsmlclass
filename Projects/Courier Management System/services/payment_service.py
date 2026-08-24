# services/payment_service.py
# Business logic for Payment / Charges module

from database import load_data, save_data
from models import Payment
from services.parcel_service import find_parcel_by_tracking_no

FILENAME = "payments.json"


class ParcelNotFoundError(Exception):
    """Raised when a payment references a tracking_no that doesn't exist."""
    pass


class InvalidPaymentError(Exception):
    """Raised when payment details are invalid (e.g. zero/negative amount)."""
    pass


def add_payment(tracking_no, amount, method, status="Paid"):
    """
    Records a payment against an existing parcel.
    Validates the parcel exists and the amount is positive.
    """
    parcel = find_parcel_by_tracking_no(tracking_no)
    if parcel is None:
        raise ParcelNotFoundError(f"No parcel found with tracking number {tracking_no}")

    if amount is None or amount <= 0:
        raise InvalidPaymentError("Payment amount must be greater than zero.")

    data = load_data(FILENAME)
    if "payments" not in data:
        data = {"next_id": 1, "payments": []}

    new_id = data["next_id"]

    from datetime import date
    payment = Payment(new_id, tracking_no, amount, method, status, str(date.today()))

    data["payments"].append(payment.to_dict())
    data["next_id"] += 1

    save_data(FILENAME, data)
    return payment


def get_all_payments():
    data = load_data(FILENAME)
    return data.get("payments", [])


def find_payments_by_tracking_no(tracking_no):
    """
    A parcel could theoretically have more than one payment record
    (e.g. original payment + a refund entry), so this returns a list.
    """
    return [p for p in get_all_payments() if p["tracking_no"] == tracking_no]


def refund_payment(payment_id):
    """
    Marks a payment as Refunded. Only allowed if it's currently 'Paid'.
    """
    data = load_data(FILENAME)
    payments = data.get("payments", [])

    for p in payments:
        if p["payment_id"] == payment_id:
            if p["status"] != "Paid":
                raise InvalidPaymentError(f"Cannot refund a payment with status '{p['status']}'.")
            p["status"] = "Refunded"
            save_data(FILENAME, data)
            return True

    raise ValueError(f"No payment found with ID {payment_id}")


def search_payments(keyword):
    keyword = keyword.lower()
    return [
        p for p in get_all_payments()
        if keyword in p["tracking_no"].lower()
        or keyword in p["method"].lower()
        or keyword in p["status"].lower()
    ]