# views/parcel_view.py
# Tkinter UI for Parcel Registration

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.parcel_service import (
    add_parcel, get_all_parcels, update_parcel, delete_parcel,
    search_parcels, CustomerNotFoundError
)


class ParcelView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_tracking_no = None

        self._build_form()
        self._build_buttons()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        labels = [
            "Customer ID", "Sender Name", "Receiver Name", "Receiver Phone",
            "Pickup Address", "Destination Address", "Weight (kg)", "Dimensions",
            "Delivery Charge", "Expected Delivery (YYYY-MM-DD)"
        ]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[label] = entry

        # Courier Type dropdown
        tk.Label(form_frame, text="Courier Type").grid(row=len(labels), column=0, sticky="e", padx=5, pady=2)
        self.courier_type_var = tk.StringVar(value="Standard")
        ttk.Combobox(
            form_frame, textvariable=self.courier_type_var,
            values=["Standard", "Express", "Same Day"], state="readonly", width=27
        ).grid(row=len(labels), column=1, padx=5, pady=2)

        # Insurance dropdown
        tk.Label(form_frame, text="Insurance").grid(row=len(labels) + 1, column=0, sticky="e", padx=5, pady=2)
        self.insurance_var = tk.StringVar(value="No")
        ttk.Combobox(
            form_frame, textvariable=self.insurance_var,
            values=["Yes", "No"], state="readonly", width=27
        ).grid(row=len(labels) + 1, column=1, padx=5, pady=2)

    def _build_buttons(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Book Parcel", width=12, command=self.handle_add).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, command=self.handle_update).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, command=self.handle_delete).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10, command=self.clear_form).grid(row=0, column=3, padx=5)

        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search (Tracking No / Receiver):").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.handle_search).pack(side="left", padx=5)
        tk.Button(search_frame, text="Show All", command=self.refresh_table).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("Tracking No", "Customer ID", "Receiver", "Phone", "Destination",
                   "Weight", "Charge", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=95)

        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Button handlers ----------

    def handle_add(self):
        values = self._get_form_values()

        if not values["Customer ID"] or not values["Receiver Name"]:
            messagebox.showerror("Missing Fields", "Customer ID and Receiver Name are required.")
            return

        try:
            customer_id = int(values["Customer ID"])
        except ValueError:
            messagebox.showerror("Invalid Input", "Customer ID must be a number.")
            return

        try:
            weight = float(values["Weight (kg)"]) if values["Weight (kg)"] else 0.0
            charge = float(values["Delivery Charge"]) if values["Delivery Charge"] else 0.0
        except ValueError:
            messagebox.showerror("Invalid Input", "Weight and Delivery Charge must be numbers.")
            return

        try:
            parcel = add_parcel(
                customer_id, values["Sender Name"], values["Receiver Name"], values["Receiver Phone"],
                values["Pickup Address"], values["Destination Address"], weight, values["Dimensions"],
                self.courier_type_var.get(), self.insurance_var.get(), charge,
                str(date.today()), values["Expected Delivery (YYYY-MM-DD)"]
            )
            messagebox.showinfo("Success", f"Parcel booked. Tracking No: {parcel.get_tracking_no()}")
            self.clear_form()
            self.refresh_table()

        except CustomerNotFoundError as e:
            messagebox.showerror("Customer Not Found", str(e))

    def handle_update(self):
        if self.selected_tracking_no is None:
            messagebox.showerror("No Selection", "Select a parcel from the table first.")
            return

        values = self._get_form_values()
        try:
            weight = float(values["Weight (kg)"]) if values["Weight (kg)"] else 0.0
            charge = float(values["Delivery Charge"]) if values["Delivery Charge"] else 0.0
        except ValueError:
            messagebox.showerror("Invalid Input", "Weight and Delivery Charge must be numbers.")
            return

        update_parcel(
            self.selected_tracking_no,
            sender_name=values["Sender Name"], receiver_name=values["Receiver Name"],
            receiver_phone=values["Receiver Phone"], pickup_address=values["Pickup Address"],
            destination_address=values["Destination Address"], weight=weight,
            dimensions=values["Dimensions"], courier_type=self.courier_type_var.get(),
            insurance=self.insurance_var.get(), delivery_charge=charge,
            expected_delivery=values["Expected Delivery (YYYY-MM-DD)"]
        )
        messagebox.showinfo("Success", "Parcel updated.")
        self.clear_form()
        self.refresh_table()

    def handle_delete(self):
        if self.selected_tracking_no is None:
            messagebox.showerror("No Selection", "Select a parcel from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this parcel?"):
            delete_parcel(self.selected_tracking_no)
            messagebox.showinfo("Deleted", "Parcel removed.")
            self.clear_form()
            self.refresh_table()

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        self._populate_table(search_parcels(keyword))

    # ---------- Helpers ----------

    def _get_form_values(self):
        return {label: entry.get().strip() for label, entry in self.entries.items()}

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.courier_type_var.set("Standard")
        self.insurance_var.set("No")
        self.selected_tracking_no = None

    def refresh_table(self):
        self._populate_table(get_all_parcels())

    def _populate_table(self, parcels):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in parcels:
            self.tree.insert("", tk.END, values=(
                p["tracking_no"], p["customer_id"], p["receiver_name"], p["receiver_phone"],
                p["destination_address"], p["weight"], p["delivery_charge"], p["status"]
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.selected_tracking_no = values[0]

        self.entries["Customer ID"].delete(0, tk.END)
        self.entries["Customer ID"].insert(0, values[1])
        self.entries["Receiver Name"].delete(0, tk.END)
        self.entries["Receiver Name"].insert(0, values[2])
        self.entries["Receiver Phone"].delete(0, tk.END)
        self.entries["Receiver Phone"].insert(0, values[3])
        self.entries["Destination Address"].delete(0, tk.END)
        self.entries["Destination Address"].insert(0, values[4])
        self.entries["Weight (kg)"].delete(0, tk.END)
        self.entries["Weight (kg)"].insert(0, values[5])
        self.entries["Delivery Charge"].delete(0, tk.END)
        self.entries["Delivery Charge"].insert(0, values[6])


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Parcel Registration")
    root.geometry("800x550")

    view = ParcelView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()