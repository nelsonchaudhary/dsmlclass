# views/employee_view.py
# Tkinter UI for Employee & Delivery Boy Management

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.employee_service import (
    add_employee, get_all_employees, update_employee,
    delete_employee, search_employees
)


class EmployeeView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_employee_id = None

        self._build_form()
        self._build_buttons()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        labels = ["Name", "Phone", "Email", "Address", "Department", "Salary", "Designation"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[label] = entry

        # Role dropdown — separate from the text entries since it's a fixed set of choices
        tk.Label(form_frame, text="Role").grid(row=len(labels), column=0, sticky="e", padx=5, pady=2)
        self.role_var = tk.StringVar(value="Operator")
        role_dropdown = ttk.Combobox(
            form_frame, textvariable=self.role_var,
            values=["Admin", "Operator", "DeliveryBoy"], state="readonly", width=27
        )
        role_dropdown.grid(row=len(labels), column=1, padx=5, pady=2)

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
        columns = ("ID", "Name", "Phone", "Email", "Department", "Salary", "Designation", "Role")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)

        self.tree.pack(pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ---------- Button handlers ----------

    def handle_add(self):
        values = self._get_form_values()
        if not values["Name"] or not values["Phone"]:
            messagebox.showerror("Missing Fields", "Name and Phone are required.")
            return

        add_employee(
            values["Name"], values["Phone"], values["Email"], values["Address"],
            values["Department"], values["Salary"], values["Designation"],
            str(date.today()), role=self.role_var.get()
        )
        messagebox.showinfo("Success", "Employee added.")
        self.clear_form()
        self.refresh_table()

    def handle_update(self):
        if self.selected_employee_id is None:
            messagebox.showerror("No Selection", "Select an employee from the table first.")
            return

        values = self._get_form_values()
        update_employee(
            self.selected_employee_id,
            name=values["Name"], phone=values["Phone"], email=values["Email"],
            address=values["Address"], department=values["Department"],
            salary=values["Salary"], designation=values["Designation"],
            role=self.role_var.get()
        )
        messagebox.showinfo("Success", "Employee updated.")
        self.clear_form()
        self.refresh_table()

    def handle_delete(self):
        if self.selected_employee_id is None:
            messagebox.showerror("No Selection", "Select an employee from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this employee?"):
            delete_employee(self.selected_employee_id)
            messagebox.showinfo("Deleted", "Employee removed.")
            self.clear_form()
            self.refresh_table()

    def handle_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        self._populate_table(search_employees(keyword))

    # ---------- Helpers ----------

    def _get_form_values(self):
        return {label: entry.get().strip() for label, entry in self.entries.items()}

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.role_var.set("Operator")
        self.selected_employee_id = None

    def refresh_table(self):
        self._populate_table(get_all_employees())

    def _populate_table(self, employees):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for e in employees:
            self.tree.insert("", tk.END, values=(
                e["employee_id"], e["name"], e["phone"], e["email"],
                e["department"], e["salary"], e["designation"], e["role"]
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.selected_employee_id = values[0]

        fields = ["Name", "Phone", "Email", "Department", "Salary", "Designation"]
        for i, field in enumerate(fields, start=1):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, values[i])

        self.entries["Address"].delete(0, tk.END)  # address isn't shown in table, left blank on select
        self.role_var.set(values[7])


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Employee Management")
    root.geometry("750x500")

    view = EmployeeView(root)
    view.pack(fill="both", expand=True)

    root.mainloop()