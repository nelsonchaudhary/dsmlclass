# reports/report_service.py
# Aggregates data across modules for Reports & Dashboard

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from collections import Counter

from services.customer_service import get_all_customers
from services.parcel_service import get_all_parcels
from services.payment_service import get_all_payments


def get_dashboard_summary():
    """
    Returns key numbers for the dashboard's top summary cards.
    """
    parcels = get_all_parcels()
    payments = get_all_payments()
    customers = get_all_customers()

    today_str = str(date.today())

    today_parcels = [p for p in parcels if p["booking_date"] == today_str]
    pending_parcels = [p for p in parcels if p["status"] not in ("Delivered", "Cancelled", "Returned")]
    delivered_parcels = [p for p in parcels if p["status"] == "Delivered"]
    cancelled_parcels = [p for p in parcels if p["status"] == "Cancelled"]

    total_revenue = sum(p["total"] for p in payments if p["status"] == "Paid")

    return {
        "total_customers": len(customers),
        "total_parcels": len(parcels),
        "today_parcels": len(today_parcels),
        "pending_parcels": len(pending_parcels),
        "delivered_parcels": len(delivered_parcels),
        "cancelled_parcels": len(cancelled_parcels),
        "total_revenue": round(total_revenue, 2)
    }


def get_status_breakdown():
    """
    Returns a count of parcels grouped by status.
    e.g. {"Booked": 3, "In Transit": 2, "Delivered": 10, ...}
    Used for a simple bar-style breakdown on the dashboard.
    """
    parcels = get_all_parcels()
    statuses = [p["status"] for p in parcels]
    return dict(Counter(statuses))


def get_revenue_report(period="monthly"):
    """
    Groups revenue from Paid payments by day, month, or year.
    period: "daily", "monthly", or "yearly"
    Returns a dict like {"2026-08": 1250.0, "2026-09": 800.0}
    """
    payments = get_all_payments()
    paid_payments = [p for p in payments if p["status"] == "Paid"]

    revenue_by_period = {}

    for p in paid_payments:
        payment_date = datetime.strptime(p["payment_date"], "%Y-%m-%d")

        if period == "daily":
            key = payment_date.strftime("%Y-%m-%d")
        elif period == "monthly":
            key = payment_date.strftime("%Y-%m")
        elif period == "yearly":
            key = payment_date.strftime("%Y")
        else:
            raise ValueError("period must be 'daily', 'monthly', or 'yearly'")

        revenue_by_period[key] = revenue_by_period.get(key, 0) + p["total"]

    # round all totals for clean display
    return {k: round(v, 2) for k, v in revenue_by_period.items()}


def get_customer_report():
    """
    Returns a list of customers with their total number of parcels booked.
    Useful for identifying frequent customers.
    """
    customers = get_all_customers()
    parcels = get_all_parcels()

    report = []
    for c in customers:
        parcel_count = len([p for p in parcels if p["customer_id"] == c["customer_id"]])
        report.append({
            "customer_id": c["customer_id"],
            "name": c["name"],
            "total_parcels": parcel_count
        })

    return report


def get_employee_report():
    """
    Returns delivery boys with a count of parcels assigned to them.
    """
    from services.employee_service import get_delivery_boys

    delivery_boys = get_delivery_boys()
    parcels = get_all_parcels()

    report = []
    for boy in delivery_boys:
        assigned_count = len([
            p for p in parcels if p.get("assigned_delivery_boy") == boy["employee_id"]
        ])
        report.append({
            "employee_id": boy["employee_id"],
            "name": boy["name"],
            "assigned_parcels": assigned_count
        })

    return report