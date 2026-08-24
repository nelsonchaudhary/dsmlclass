# views/delivery_view.py
# Tkinter UI for Delivery Management: assign delivery boy, confirm delivery via OTP

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox

from services.parcel_service import (
    get_all_parcels, find_parcel_by_tracking_no, assign_delivery_boy,
    confirm_delivery, get_available_delivery_boys,
    DeliveryBoyNotFoundError, InvalidStatusTransitionError, InvalidOTPError
)


class DeliveryView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_tracking_no = None

        self._build_assign_panel()
        self._build_confirm_panel()
        self._build_table()
        self.refresh_table()

    def _build_assign_panel(self):
        frame = tk.LabelFrame(self, text="Assign Delivery Boy")
        frame.pack(pady=10, padx=10, fill="x")

        tk.Label(frame, text="Delivery Boy:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.delivery_boy_var = tk.StringVar()
        self.delivery_boy_dropdown = ttk.Combobox(
            frame, textvariable=self.delivery_boy_var, state="readonly", width=35
        )
        self.delivery_boy_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self._load_delivery_boys()

        tk.Button(frame, text="Assign", command=self.handle_assign).grid(row=0, column=2, padx=10)

    def _build_confirm_panel(self):
        frame = tk.LabelFrame(self, text="Confirm Delivery")
        frame.pack(pady=10, padx=10, fill="x")

        tk.Label(frame, text="Enter OTP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.otp_entry = tk.Entry(frame, width=15)
        self.otp_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame, text="Received By:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.received_by_entry = tk.Entry(frame, width=25)
        self.received_by_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Button(frame, text="Confirm Delivery", command=self.handle_confirm).grid(row=0, column=2, rowspan=2, padx=10)

    def _build_table(self):
        columns = ("Tracking No", "Receiver", "Status", "Assigned Delivery Boy")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack(pady=10, padx=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Handlers ----------

    def _load_delivery_boys(self):
        boys = get_available_delivery_boys()
        # Store as "ID - Name" strings for the dropdown, but keep a lookup back to the ID
        self.boy_lookup = {f"{b['employee_id']} - {b['name']}": b['employee_id'] for b in boys}
        self.delivery_boy_dropdown["values"] = list(self.boy_lookup.keys())

    def handle_assign(self):
        if self.selected_tracking_no is None:
            messagebox.showerror("No Selection", "Select a parcel from the table first.")
            return

        choice = self.delivery_boy_var.get()
        if not choice:
            messagebox.showerror("No Delivery Boy", "Choose a delivery boy from the dropdown.")
            return

        employee_id = self.boy_lookup[choice]

        try:
            otp = assign_delivery_boy(self.selected_tracking_no, employee_id)
            messagebox.showinfo(
                "Assigned",
                f"Delivery boy assigned.\nOTP for delivery confirmation: {otp}\n"
                f"(In a real system this would be sent to the receiver via SMS.)"
            )
            self.refresh_table()

        except DeliveryBoyNotFoundError as e:
            messagebox.showerror("Error", str(e))

    def handle_confirm(self):
        if self.selected_tracking_no is None:
            messagebox.showerror("No Selection", "Select a parcel from the table first.")
            return

        otp = self.otp_entry.get().strip()
        received_by = self.received_by_entry.get().strip()

        if not otp or not received_by:
            messagebox.showerror("Missing Fields", "Enter both OTP and Received By name.")
            return

        try:
            confirm_delivery(self.selected_tracking_no, otp, received_by)
            messagebox.showinfo("Delivered", f"Parcel {self.selected_tracking_no} marked as Delivered.")
            self.otp_entry.delete(0, tk.END)
            self.received_by_entry.delete(0, tk.END)
            self.refresh_table()

        except InvalidStatusTransitionError as e:
            messagebox.showerror("Wrong Status", str(e))
        except InvalidOTPError as e:
            messagebox.showerror("Invalid OTP", str(e))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.selected_tracking_no = values[0]

    # ---------- Table ----------

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in get_all_parcels():
            assigned = p.get("assigned_delivery_boy")
            assigned_display = assigned if assigned else "Not Assigned"
            self.tree.insert("", tk.END, values=(
                p["tracking_no"], p["receiver_name"], p["status"], assigned_display
            ))


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Delivery Management")
    root.geometry("700x500")

    view = DeliveryView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()