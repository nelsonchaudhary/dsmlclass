# main.py
# Entry point of the application.
# Shows Login first, then a main window with sidebar navigation
# to every module, based on the logged-in user's role.

import tkinter as tk
from tkinter import messagebox

from config import APP_TITLE
from views.login_view import LoginView
from views.customer_view import CustomerView
from views.employee_view import EmployeeView
from views.parcel_view import ParcelView
from views.tracking_view import TrackingView
from views.delivery_view import DeliveryView
from views.payment_view import PaymentView
from views.global_search_view import GlobalSearchView
from views.dashboard_view import DashboardView
from views.backup_view import BackupView


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x650")

        # Set custom window/taskbar icon
        try:
            self.iconbitmap("assets/icon.ico")
        except tk.TclError:
            pass  # if the icon file is missing or invalid, just skip it silently

        self.current_user = None
        self.current_frame = None  # tracks whichever screen is currently shown

        self.show_login()

    # ---------- Screen switching ----------

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.current_frame = LoginView(self, on_success_callback=self.handle_login_success)
        self.current_frame.pack(fill="both", expand=True)

    def handle_login_success(self, user):
        self.current_user = user
        self.show_main_layout()

    def show_main_layout(self):
        self.clear_window()

        # Sidebar for navigation
        sidebar = tk.Frame(self, width=180, bg="#2c3e50")
        sidebar.pack(side="left", fill="y")

        # Right side: header on top, content area below
        right_side = tk.Frame(self)
        right_side.pack(side="right", fill="both", expand=True)

        self.header_label = tk.Label(
            right_side, text="Dashboard", font=("Arial", 16, "bold"),
            bg="#ecf0f1", anchor="w", padx=15, pady=12
        )
        self.header_label.pack(fill="x")

        self.content_area = tk.Frame(right_side)
        self.content_area.pack(fill="both", expand=True)

        tk.Label(
            sidebar, text=f"Logged in as:\n{self.current_user['username']} ({self.current_user['role']})",
            bg="#2c3e50", fg="white", wraplength=160, justify="left", pady=15
        ).pack(fill="x", padx=10)

        # Menu items available to everyone
        menu_items = [
            ("Dashboard", DashboardView),
            ("Customers", CustomerView),
            ("Parcels", ParcelView),
            ("Tracking", TrackingView),
            ("Delivery", DeliveryView),
            ("Payments", PaymentView),
            ("Global Search", GlobalSearchView),
        ]

        # Admin-only menu items (role-based access)
        if self.current_user["role"] == "Admin":
            menu_items.append(("Employees", EmployeeView))
            menu_items.append(("Backup / Export", BackupView))

        # Keep references to sidebar buttons so we can highlight the active one
        self.sidebar_buttons = {}

        for label, view_class in menu_items:
            btn = tk.Button(
                sidebar, text=label, width=20, anchor="w",
                bg="#34495e", fg="white", activebackground="#1abc9c",
                relief="flat", bd=0,
                command=lambda vc=view_class, lbl=label: self.switch_view(vc, lbl)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.sidebar_buttons[label] = btn

        tk.Button(
            sidebar, text="Logout", width=20, anchor="w", bg="#e74c3c", fg="white",
            relief="flat", bd=0, command=self.handle_logout
        ).pack(fill="x", padx=10, pady=(20, 5))

        # Show Dashboard by default after login
        self.switch_view(DashboardView, "Dashboard")

    def switch_view(self, view_class, label):
        """
        Clears the content area, loads the new module's screen,
        updates the header text, and highlights the active sidebar button.
        """
        for widget in self.content_area.winfo_children():
            widget.destroy()

        view = view_class(self.content_area)
        view.pack(fill="both", expand=True, padx=10, pady=10)

        # Update header text
        self.header_label.config(text=label)

        # Reset all sidebar buttons to default color, then highlight the active one
        for btn_label, btn in self.sidebar_buttons.items():
            if btn_label == label:
                btn.config(bg="#1abc9c")   # active = teal highlight
            else:
                btn.config(bg="#34495e")   # inactive = default dark

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.show_login()


def main():
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()