# views/dashboard_view.py
# Tkinter UI for Dashboard & Reports

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk

from reports.report_service import (
    get_dashboard_summary, get_status_breakdown, get_revenue_report,
    get_customer_report, get_employee_report
)


class DashboardView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self._build_summary_cards()
        self._build_status_breakdown()
        self._build_report_tabs()
        self.refresh_all()

    def _build_summary_cards(self):
        self.summary_frame = tk.Frame(self)
        self.summary_frame.pack(pady=10, fill="x")

        # Labels are created empty here and filled in refresh_all()
        self.card_labels = {}
        card_titles = [
            "total_customers", "total_parcels", "today_parcels",
            "pending_parcels", "delivered_parcels", "total_revenue"
        ]

        for i, key in enumerate(card_titles):
            card = tk.LabelFrame(self.summary_frame, text=key.replace("_", " ").title(), padx=10, pady=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            label = tk.Label(card, text="0", font=("Arial", 14, "bold"))
            label.pack()
            self.card_labels[key] = label

    def _build_status_breakdown(self):
        frame = tk.LabelFrame(self, text="Parcels by Status", padx=10, pady=10)
        frame.pack(pady=10, padx=10, fill="x")

        self.status_tree = ttk.Treeview(frame, columns=("Status", "Count"), show="headings", height=5)
        self.status_tree.heading("Status", text="Status")
        self.status_tree.heading("Count", text="Count")
        self.status_tree.column("Status", width=150)
        self.status_tree.column("Count", width=100)
        self.status_tree.pack()

    def _build_report_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Revenue report tab
        revenue_tab = tk.Frame(self.notebook)
        self.notebook.add(revenue_tab, text="Revenue Report")

        period_frame = tk.Frame(revenue_tab)
        period_frame.pack(pady=5)
        tk.Label(period_frame, text="Group by:").pack(side="left", padx=5)
        self.period_var = tk.StringVar(value="monthly")
        ttk.Combobox(
            period_frame, textvariable=self.period_var,
            values=["daily", "monthly", "yearly"], state="readonly", width=15
        ).pack(side="left", padx=5)
        tk.Button(period_frame, text="Generate", command=self.refresh_revenue).pack(side="left", padx=5)

        self.revenue_tree = ttk.Treeview(revenue_tab, columns=("Period", "Revenue"), show="headings", height=8)
        self.revenue_tree.heading("Period", text="Period")
        self.revenue_tree.heading("Revenue", text="Revenue")
        self.revenue_tree.pack(pady=5, padx=5, fill="both", expand=True)

        # Customer report tab
        customer_tab = tk.Frame(self.notebook)
        self.notebook.add(customer_tab, text="Customer Report")

        self.customer_report_tree = ttk.Treeview(
            customer_tab, columns=("ID", "Name", "Total Parcels"), show="headings", height=10
        )
        for col in ("ID", "Name", "Total Parcels"):
            self.customer_report_tree.heading(col, text=col)
        self.customer_report_tree.pack(pady=5, padx=5, fill="both", expand=True)

        # Employee report tab
        employee_tab = tk.Frame(self.notebook)
        self.notebook.add(employee_tab, text="Employee Report")

        self.employee_report_tree = ttk.Treeview(
            employee_tab, columns=("ID", "Name", "Assigned Parcels"), show="headings", height=10
        )
        for col in ("ID", "Name", "Assigned Parcels"):
            self.employee_report_tree.heading(col, text=col)
        self.employee_report_tree.pack(pady=5, padx=5, fill="both", expand=True)

    # ---------- Refresh logic ----------

    def refresh_all(self):
        self.refresh_summary()
        self.refresh_status_breakdown()
        self.refresh_revenue()
        self.refresh_customer_report()
        self.refresh_employee_report()

    def refresh_summary(self):
        summary = get_dashboard_summary()
        for key, label in self.card_labels.items():
            label.config(text=str(summary[key]))

    def refresh_status_breakdown(self):
        for row in self.status_tree.get_children():
            self.status_tree.delete(row)

        breakdown = get_status_breakdown()
        for status, count in breakdown.items():
            self.status_tree.insert("", tk.END, values=(status, count))

    def refresh_revenue(self):
        for row in self.revenue_tree.get_children():
            self.revenue_tree.delete(row)

        revenue = get_revenue_report(self.period_var.get())
        for period, amount in sorted(revenue.items()):
            self.revenue_tree.insert("", tk.END, values=(period, amount))

    def refresh_customer_report(self):
        for row in self.customer_report_tree.get_children():
            self.customer_report_tree.delete(row)

        for c in get_customer_report():
            self.customer_report_tree.insert("", tk.END, values=(
                c["customer_id"], c["name"], c["total_parcels"]
            ))

    def refresh_employee_report(self):
        for row in self.employee_report_tree.get_children():
            self.employee_report_tree.delete(row)

        for e in get_employee_report():
            self.employee_report_tree.insert("", tk.END, values=(
                e["employee_id"], e["name"], e["assigned_parcels"]
            ))


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dashboard")
    root.geometry("850x650")

    view = DashboardView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()