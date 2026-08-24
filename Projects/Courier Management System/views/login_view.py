# views/login_view.py
# Tkinter Login screen (Module 1)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox

from services.auth_service import login, InvalidLoginError, WrongPasswordError


class LoginView(tk.Frame):
    """
    on_success_callback: a function passed in from main.py,
    called with the logged-in user's dict once login succeeds.
    This is how LoginView hands control back to the main app
    without needing to know anything about the rest of the app.
    """

    def __init__(self, master, on_success_callback):
        super().__init__(master, bg="#2c3e50")
        self.master = master
        self.on_success_callback = on_success_callback

        self.show_password = False  # tracks show/hide password toggle state

        self._build_ui()

    def _build_ui(self):
        # Outer frame fills the whole window with the dark navy background
        self.pack(fill="both", expand=True)

        # Centered white "card" holding the actual form
        card = tk.Frame(self, bg="white", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # App title
        tk.Label(
            card, text="Courier Management System",
            font=("Arial", 16, "bold"), bg="white", fg="#2c3e50"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 5))

        tk.Label(
            card, text="Sign in to continue",
            font=("Arial", 10), bg="white", fg="#7f8c8d"
        ).grid(row=1, column=0, columnspan=2, pady=(0, 25))

        # Username field
        tk.Label(card, text="Username", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 3)
        )
        self.username_entry = tk.Entry(
            card, width=30, font=("Arial", 11), relief="solid", bd=1,
            highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#1abc9c"
        )
        self.username_entry.grid(row=3, column=0, columnspan=2, ipady=6, pady=(0, 15))

        # Password field + show/hide toggle
        tk.Label(card, text="Password", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", anchor="w").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(0, 3)
        )
        self.password_entry = tk.Entry(
            card, width=30, font=("Arial", 11), show="*", relief="solid", bd=1,
            highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#1abc9c"
        )
        self.password_entry.grid(row=5, column=0, columnspan=2, ipady=6, pady=(0, 5))
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

        self.toggle_btn = tk.Button(
            card, text="Show password", font=("Arial", 8), bg="white", fg="#1abc9c",
            relief="flat", bd=0, cursor="hand2", command=self.toggle_password_visibility
        )
        self.toggle_btn.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Login button
        login_btn = tk.Button(
            card, text="Login", font=("Arial", 11, "bold"), bg="#1abc9c", fg="white",
            relief="flat", bd=0, cursor="hand2", command=self.handle_login
        )
        login_btn.grid(row=7, column=0, columnspan=2, sticky="ew", ipady=8)

        # Hover effect on the login button
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#16a085"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#1abc9c"))

        # Default credentials hint
        tk.Label(
            card, text="Default: admin / admin123",
            font=("Arial", 8), bg="white", fg="#95a5a6"
        ).grid(row=8, column=0, columnspan=2, pady=(15, 0))

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_btn.config(text="Hide password")
        else:
            self.password_entry.config(show="*")
            self.toggle_btn.config(text="Show password")

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Missing Fields", "Enter both username and password.")
            return

        try:
            user = login(username, password)
            self.on_success_callback(user)   # hand control back to main.py

        except InvalidLoginError as e:
            messagebox.showerror("Login Failed", str(e))
        except WrongPasswordError as e:
            messagebox.showerror("Login Failed", str(e))