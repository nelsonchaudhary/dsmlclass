# views/global_search_view.py
# Tkinter UI for Global Search & Filter across Customers, Parcels, and Payments

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk

from services.customer_service import search_customers
from services.parcel_service import search_parcels
from services.payment_service import search_payments


class GlobalSearchView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self._build_search_bar()
        self._build_result_tabs()

    def _build_search_bar(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Search everything:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.search_entry = tk.Entry(frame, width=35)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.handle_search())  # Enter key triggers search too

        tk.Button(frame, text="Search", command=self.handle_search).pack(side="left", padx=5)
        tk.Button(frame, text="Clear", command=self.handle_clear).pack(side="left", padx=5)

    def _build_result_tabs(self):
        """
        Uses a Notebook (tabbed view) — one tab per module's results,
        so all three result sets are visible without cluttering one table.
        """
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Customers tab
        self.customer_tree = self._make_result_tree(
            "Customers", ("ID", "Name", "Phone", "Email", "City")
        )

        # Parcels tab
        self.parcel_tree = self._make_result_tree(
            "Parcels", ("Tracking No", "Receiver", "Phone", "Destination", "Status")
        )

        # Payments tab
        self.payment_tree = self._make_result_tree(
            "Payments", ("Payment ID", "Tracking No", "Amount", "Method", "Status")
        )

    def _make_result_tree(self, tab_name, columns):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)

        tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        return tree

    # ---------- Handlers ----------

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            return

        customers = search_customers(keyword)
        parcels = search_parcels(keyword)
        payments = search_payments(keyword)

        self._fill_tree(self.customer_tree, customers,
                         lambda c: (c["customer_id"], c["name"], c["phone"], c["email"], c["city"]))

        self._fill_tree(self.parcel_tree, parcels,
                         lambda p: (p["tracking_no"], p["receiver_name"], p["receiver_phone"],
                                    p["destination_address"], p["status"]))

        self._fill_tree(self.payment_tree, payments,
                         lambda p: (p["payment_id"], p["tracking_no"], p["amount"], p["method"], p["status"]))

        # Auto-switch to whichever tab actually has results, so the user
        # doesn't have to manually click through all three tabs
        self._focus_tab_with_results(customers, parcels, payments)

    def _fill_tree(self, tree, records, row_mapper):
        for row in tree.get_children():
            tree.delete(row)
        for record in records:
            tree.insert("", tk.END, values=row_mapper(record))

    def _focus_tab_with_results(self, customers, parcels, payments):
        if customers:
            self.notebook.select(0)
        elif parcels:
            self.notebook.select(1)
        elif payments:
            self.notebook.select(2)
        # if nothing matched anywhere, leave the tab as-is; tables will just be empty

    def handle_clear(self):
        self.search_entry.delete(0, tk.END)
        for tree in (self.customer_tree, self.parcel_tree, self.payment_tree):
            for row in tree.get_children():
                tree.delete(row)


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Global Search")
    root.geometry("700x500")

    view = GlobalSearchView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()