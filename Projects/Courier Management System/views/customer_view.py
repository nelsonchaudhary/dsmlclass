# views/customer_view.py
# Tkinter UI for Customer Management module
import sys
import os

# Add the project root folder to Python's search path
# so "services" and other root-level packages can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.customer_service import (
    add_customer, get_all_customers, update_customer,
    delete_customer, search_customers
)


class CustomerView(tk.Frame):
    """
    A Tkinter Frame containing the full Customer Management screen.
    Can be embedded inside a main app window later, or run standalone for testing.
    """

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_customer_id = None  # tracks which row is selected for update/delete

        self._build_form()
        self._build_buttons()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        labels = ["Name", "Phone", "Email", "Address", "City", "Postal Code"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[label] = entry

    def _build_buttons(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add", width=10, command=self.handle_add).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=10, command=self.handle_update).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=10, command=self.handle_delete).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", width=10, command=self.clear_form).grid(row=0, column=3, padx=5)

        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.handle_search).pack(side="left", padx=5)
        tk.Button(search_frame, text="Show All", command=self.refresh_table).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("ID", "Name", "Phone", "Email", "Address", "City", "Postal Code")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Button handlers ----------

    def handle_add(self):
        values = self._get_form_values()
        if not values["Name"] or not values["Phone"]:
            messagebox.showerror("Missing Fields", "Name and Phone are required.")
            return

        add_customer(
            values["Name"], values["Phone"], values["Email"],
            values["Address"], values["City"], values["Postal Code"],
            str(date.today())
        )
        messagebox.showinfo("Success", "Customer added.")
        self.clear_form()
        self.refresh_table()

    def handle_update(self):
        if self.selected_customer_id is None:
            messagebox.showerror("No Selection", "Select a customer from the table first.")
            return

        values = self._get_form_values()
        update_customer(
            self.selected_customer_id,
            name=values["Name"], phone=values["Phone"], email=values["Email"],
            address=values["Address"], city=values["City"], postal_code=values["Postal Code"]
        )
        messagebox.showinfo("Success", "Customer updated.")
        self.clear_form()
        self.refresh_table()

    def handle_delete(self):
        if self.selected_customer_id is None:
            messagebox.showerror("No Selection", "Select a customer from the table first.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this customer?")
        if confirm:
            delete_customer(self.selected_customer_id)
            messagebox.showinfo("Deleted", "Customer removed.")
            self.clear_form()
            self.refresh_table()

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        results = search_customers(keyword)
        self._populate_table(results)

    # ---------- Helpers ----------

    def _get_form_values(self):
        return {label: entry.get().strip() for label, entry in self.entries.items()}

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_customer_id = None

    def refresh_table(self):
        customers = get_all_customers()
        self._populate_table(customers)

    def _populate_table(self, customers):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for c in customers:
            self.tree.insert("", tk.END, values=(
                c["customer_id"], c["name"], c["phone"],
                c["email"], c["address"], c["city"], c["postal_code"]
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.selected_customer_id = values[0]

        self.entries["Name"].delete(0, tk.END)
        self.entries["Name"].insert(0, values[1])
        self.entries["Phone"].delete(0, tk.END)
        self.entries["Phone"].insert(0, values[2])
        self.entries["Email"].delete(0, tk.END)
        self.entries["Email"].insert(0, values[3])
        self.entries["Address"].delete(0, tk.END)
        self.entries["Address"].insert(0, values[4])
        self.entries["City"].delete(0, tk.END)
        self.entries["City"].insert(0, values[5])
        self.entries["Postal Code"].delete(0, tk.END)
        self.entries["Postal Code"].insert(0, values[6])


# Standalone test — lets you run just this screen without the full app
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Customer Management")
    root.geometry("650x500")

    view = CustomerView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()