# views/tracking_view.py
# Tkinter UI for updating parcel shipment status (Shipment Tracking module)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox

from services.parcel_service import (
    get_all_parcels, find_parcel_by_tracking_no, get_next_statuses,
    update_parcel_status, InvalidStatusTransitionError
)


class TrackingView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_tracking_no = None

        self._build_search()
        self._build_status_panel()
        self._build_table()
        self.refresh_table()

    def _build_search(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Tracking No:").pack(side="left", padx=5)
        self.tracking_entry = tk.Entry(frame, width=20)
        self.tracking_entry.pack(side="left", padx=5)
        tk.Button(frame, text="Load Parcel", command=self.handle_load).pack(side="left", padx=5)
        tk.Button(frame, text="Show All", command=self.refresh_table).pack(side="left", padx=5)

    def _build_status_panel(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        self.current_status_label = tk.Label(frame, text="Current Status: -", font=("Arial", 10, "bold"))
        self.current_status_label.pack(side="left", padx=10)

        tk.Label(frame, text="Move to:").pack(side="left", padx=5)
        self.next_status_var = tk.StringVar()
        self.next_status_dropdown = ttk.Combobox(
            frame, textvariable=self.next_status_var, values=[], state="readonly", width=20
        )
        self.next_status_dropdown.pack(side="left", padx=5)

        tk.Button(frame, text="Update Status", command=self.handle_status_update).pack(side="left", padx=5)

    def _build_table(self):
        columns = ("Tracking No", "Receiver", "Destination", "Status", "Expected Delivery")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Handlers ----------

    def handle_load(self):
        tracking_no = self.tracking_entry.get().strip()
        parcel = find_parcel_by_tracking_no(tracking_no)

        if parcel is None:
            messagebox.showerror("Not Found", f"No parcel found with tracking number {tracking_no}")
            return

        self._select_parcel(tracking_no)

    def handle_status_update(self):
        if self.selected_tracking_no is None:
            messagebox.showerror("No Selection", "Load or select a parcel first.")
            return

        new_status = self.next_status_var.get()
        if not new_status:
            messagebox.showerror("No Status Chosen", "Pick a status to move to.")
            return

        try:
            update_parcel_status(self.selected_tracking_no, new_status)
            messagebox.showinfo("Updated", f"Parcel {self.selected_tracking_no} is now '{new_status}'")
            self.refresh_table()
            self._select_parcel(self.selected_tracking_no)  # reload to refresh dropdown options

        except InvalidStatusTransitionError as e:
            messagebox.showerror("Invalid Transition", str(e))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self._select_parcel(values[0])

    def _select_parcel(self, tracking_no):
        parcel = find_parcel_by_tracking_no(tracking_no)
        if parcel is None:
            return

        self.selected_tracking_no = tracking_no
        self.current_status_label.config(text=f"Current Status: {parcel['status']}")

        next_options = get_next_statuses(tracking_no)
        self.next_status_dropdown["values"] = next_options

        if next_options:
            self.next_status_var.set(next_options[0])
        else:
            self.next_status_var.set("")
            messagebox.showinfo("Final State", f"Parcel is '{parcel['status']}' — no further status changes possible.")

    # ---------- Table ----------

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in get_all_parcels():
            self.tree.insert("", tk.END, values=(
                p["tracking_no"], p["receiver_name"], p["destination_address"],
                p["status"], p["expected_delivery"]
            ))


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Shipment Tracking")
    root.geometry("750x500")

    view = TrackingView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()