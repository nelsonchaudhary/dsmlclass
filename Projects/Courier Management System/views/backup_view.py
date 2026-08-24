# views/backup_view.py
# Tkinter UI for Backup / Export module

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox

from utils.export_utils import export_to_csv
from services.customer_service import get_all_customers
from services.parcel_service import get_all_parcels
from services.payment_service import get_all_payments
from services.employee_service import get_all_employees


class BackupView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Backup / Export Data", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self, text="Export any module's data to a CSV file.").pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame, text="Export Customers", width=20,
            command=lambda: self.handle_export("customers", get_all_customers())
        ).grid(row=0, column=0, padx=10, pady=5)

        tk.Button(
            button_frame, text="Export Parcels", width=20,
            command=lambda: self.handle_export("parcels", get_all_parcels())
        ).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(
            button_frame, text="Export Payments", width=20,
            command=lambda: self.handle_export("payments", get_all_payments())
        ).grid(row=1, column=0, padx=10, pady=5)

        tk.Button(
            button_frame, text="Export Employees", width=20,
            command=lambda: self.handle_export("employees", get_all_employees())
        ).grid(row=1, column=1, padx=10, pady=5)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(pady=10)

    def handle_export(self, name, records):
        if not records:
            messagebox.showwarning("No Data", f"There are no {name} to export yet.")
            return

        file_path = export_to_csv(records, name)

        if file_path:
            messagebox.showinfo("Export Successful", f"Saved to:\n{file_path}")
            self.status_label.config(text=f"Last export: {file_path}")
        else:
            messagebox.showerror("Export Failed", f"Could not export {name}. Check app.log for details.")


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Backup / Export")
    root.geometry("500x350")

    view = BackupView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()