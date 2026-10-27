"""login.py - Login / Register window."""
import tkinter as tk
from tkinter import messagebox

import database
import info
from theme import BG, PRIMARY, DARK, GRAY, TEXT, SOFT, FONT, FONT_BOLD, make_button, card


class LoginWindow(tk.Tk):                      # inherits from tk.Tk (Inheritance)
    def __init__(self):
        super().__init__()
        self.title(f"Expense Tracker - {info.UID}")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.success = False
        self.username = None

        # top bar with the student UID
        bar = tk.Frame(self, bg=DARK, height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Expense Tracker", bg=DARK, fg="white",
                 font=(FONT_BOLD, 12)).pack(side="left", padx=22)
        tk.Label(bar, text=f"UID  {info.UID}", bg="#3a3a3c", fg="white",
                 font=(FONT_BOLD, 10), padx=12, pady=4).pack(side="right", padx=22)

        # white login card
        box = card(self)
        box.pack(fill="both", expand=True, padx=40, pady=(28, 12))
        tk.Label(box, text="💰", bg="white", font=(FONT, 40)).pack(pady=(26, 0))
        tk.Label(box, text="Sign in", bg="white", fg=TEXT,
                 font=(FONT_BOLD, 22)).pack()
        tk.Label(box, text="Login or create a new account", bg="white", fg=GRAY,
                 font=(FONT, 10)).pack(pady=(2, 6))

        self.user_entry = self.make_field(box, "Username")
        self.pass_entry = self.make_field(box, "Password", show="*")

        make_button(box, "Login", PRIMARY, self.login, width=30).pack(pady=(26, 8))
        make_button(box, "Create Account", SOFT, self.register, width=30, fg=TEXT).pack()

        tk.Label(self, text=f"{info.NAME}   •   {info.UID}", bg=BG, fg=GRAY,
                 font=(FONT, 9)).pack(pady=(0, 14))

        self.bind("<Return>", lambda event: self.login())
        self.user_entry.focus()

    def make_field(self, parent, label, show=""):
        tk.Label(parent, text=label, bg="white", fg=GRAY,
                 font=(FONT, 9)).pack(anchor="w", padx=30, pady=(14, 3))
        entry = tk.Entry(parent, show=show, font=(FONT, 11), relief="flat", bg="#fbfbfd",
                         highlightthickness=1, highlightbackground="#d2d2d7",
                         highlightcolor=PRIMARY)
        entry.pack(fill="x", padx=30, ipady=8)
        return entry

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showwarning("Missing data", "Please enter username and password.")
            return
        if database.check_login(username, password):
            self.success = True
            self.username = username
            self.destroy()
        else:
            messagebox.showerror("Login failed", "Wrong username or password.")

    def register(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        if len(username) < 3 or len(password) < 4:
            messagebox.showwarning("Weak data", "Username: min 3 chars. Password: min 4 chars.")
            return
        if database.register_user(username, password):
            messagebox.showinfo("Success", "Account created! You can now log in.")
        else:
            messagebox.showerror("Error", "That username already exists.")