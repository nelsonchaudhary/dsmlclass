# views/payment_view.py
# Tkinter UI for Payment / Charges module

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox

from services.payment_service import (
    add_payment, get_all_payments, refund_payment, search_payments,
    ParcelNotFoundError, InvalidPaymentError
)
from services.parcel_service import find_parcel_by_tracking_no


class PaymentView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_payment_id = None

        self._build_form()
        self._build_buttons()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Tracking No").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.tracking_entry = tk.Entry(frame, width=25)
        self.tracking_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(frame, text="Auto-fill Amount", command=self.autofill_amount).grid(row=0, column=2, padx=5)

        tk.Label(frame, text="Amount").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.amount_entry = tk.Entry(frame, width=25)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="Method").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.method_var = tk.StringVar(value="Cash")
        ttk.Combobox(
            frame, textvariable=self.method_var,
            values=["Cash", "Online", "COD"], state="readonly", width=22
        ).grid(row=2, column=1, padx=5, pady=2)

        tk.Label(frame, text="Status").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.status_var = tk.StringVar(value="Paid")
        ttk.Combobox(
            frame, textvariable=self.status_var,
            values=["Paid", "Pending"], state="readonly", width=22
        ).grid(row=3, column=1, padx=5, pady=2)

    def _build_buttons(self):
        frame = tk.Frame(self)
        frame.pack(pady=5)

        tk.Button(frame, text="Record Payment", width=15, command=self.handle_add).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Refund Selected", width=15, command=self.handle_refund).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Clear", width=10, command=self.clear_form).grid(row=0, column=2, padx=5)

        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.handle_search).pack(side="left", padx=5)
        tk.Button(search_frame, text="Show All", command=self.refresh_table).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("Payment ID", "Tracking No", "Amount", "VAT", "Total", "Method", "Status", "Date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)

        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Handlers ----------

    def autofill_amount(self):
        tracking_no = self.tracking_entry.get().strip()
        parcel = find_parcel_by_tracking_no(tracking_no)

        if parcel is None:
            messagebox.showerror("Not Found", f"No parcel found with tracking number {tracking_no}")
            return

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(parcel["delivery_charge"]))

    def handle_add(self):
        tracking_no = self.tracking_entry.get().strip()
        amount_str = self.amount_entry.get().strip()

        if not tracking_no or not amount_str:
            messagebox.showerror("Missing Fields", "Tracking No and Amount are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        try:
            payment = add_payment(tracking_no, amount, self.method_var.get(), self.status_var.get())
            messagebox.showinfo(
                "Success",
                f"Payment recorded.\nVAT: {payment._vat}\nTotal: {payment.get_total()}"
            )
            self.clear_form()
            self.refresh_table()

        except ParcelNotFoundError as e:
            messagebox.showerror("Parcel Not Found", str(e))
        except InvalidPaymentError as e:
            messagebox.showerror("Invalid Payment", str(e))

    def handle_refund(self):
        if self.selected_payment_id is None:
            messagebox.showerror("No Selection", "Select a payment from the table first.")
            return

        if not messagebox.askyesno("Confirm", "Refund this payment?"):
            return

        try:
            refund_payment(self.selected_payment_id)
            messagebox.showinfo("Refunded", "Payment marked as refunded.")
            self.clear_form()
            self.refresh_table()
        except InvalidPaymentError as e:
            messagebox.showerror("Cannot Refund", str(e))

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        self._populate_table(search_payments(keyword))

    # ---------- Helpers ----------

    def clear_form(self):
        self.tracking_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.method_var.set("Cash")
        self.status_var.set("Paid")
        self.selected_payment_id = None

    def refresh_table(self):
        self._populate_table(get_all_payments())

    def _populate_table(self, payments):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in payments:
            self.tree.insert("", tk.END, values=(
                p["payment_id"], p["tracking_no"], p["amount"], p["vat"],
                p["total"], p["method"], p["status"], p["payment_date"]
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.selected_payment_id = values[0]


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Payment Management")
    root.geometry("800x500")

    view = PaymentView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()