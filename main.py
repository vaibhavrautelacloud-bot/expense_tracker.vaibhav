"""main.py - run this file to start the application."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import database
import reports
import charts
from login import LoginWindow
from theme import (BG, PRIMARY, DARK, GREEN, RED, ORANGE, GRAY, FONT,
                   apply_style, make_button, stat_card)

CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Health", "Entertainment", "Others"]


class ExpenseApp(tk.Tk):                       # inherits from tk.Tk (Inheritance)
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.selected_id = None
        now = datetime.now()
        self.view_month, self.view_year = now.month, now.year   # month shown in analysis
        self.title("Personal Expense Tracker and Analysis System")
        self.geometry("1000x730")
        self.configure(bg=BG)
        apply_style(self)

        self.build_header()
        self.build_top_cards()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.tab_expenses = ttk.Frame(notebook)
        self.tab_analysis = ttk.Frame(notebook)
        notebook.add(self.tab_expenses, text="  💸 Expenses  ")
        notebook.add(self.tab_analysis, text="  📊 Analysis & Budget  ")

        self.build_expense_tab()
        self.build_analysis_tab()
        self.load_expenses()
        self.show_analysis()

    # ------------------------------------------------ HEADER + TOP CARDS
    def build_header(self):
        header = tk.Frame(self, bg=DARK, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="💰  Expense Tracker", bg=DARK, fg="white",
                 font=(FONT, 18, "bold")).pack(side="left", padx=20)
        tk.Label(header, text=f"👤  {self.username}", bg=DARK, fg="#c7d2fe",
                 font=(FONT, 12)).pack(side="right", padx=20)

    def build_top_cards(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=15, pady=12)
        c1, self.spent_val = stat_card(row, "Spent this month", PRIMARY)
        c2, self.budget_val = stat_card(row, "Monthly budget", ORANGE)
        c3, self.left_val = stat_card(row, "Remaining", GREEN)
        for card in (c1, c2, c3):
            card.pack(side="left", expand=True, fill="x", padx=6)
        self.spent_title, self.left_title = c1.title_label, c3.title_label

    # ------------------------------------------------ EXPENSE TAB
    def build_expense_tab(self):
        card = tk.Frame(self.tab_expenses, bg="white")
        card.pack(fill="x", pady=(10, 8))
        card.columnconfigure(3, weight=1)

        self.date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        self.cat_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        def field(col, text, widget):
            tk.Label(card, text=text, bg="white", fg=GRAY, font=(FONT, 9)).grid(
                row=0, column=col, sticky="w", padx=12, pady=(12, 0))
            widget.grid(row=1, column=col, sticky="ew", padx=12)

        field(0, "Date (DD-MM-YYYY)", ttk.Entry(card, textvariable=self.date_var, width=16))
        field(1, "Category", ttk.Combobox(card, textvariable=self.cat_var,
                                          values=CATEGORIES, width=16))
        field(2, "Amount (₹)", ttk.Entry(card, textvariable=self.amount_var, width=14))
        field(3, "Description", ttk.Entry(card, textvariable=self.desc_var))

        btns = tk.Frame(card, bg="white")
        btns.grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=12)
        for i, (text, color, cmd) in enumerate([
                ("Add", GREEN, self.add_expense), ("Update", PRIMARY, self.update_expense),
                ("Delete", RED, self.delete_expense), ("Clear", GRAY, self.clear_form),
                ("Export CSV", ORANGE, self.export_csv)]):
            make_button(btns, text, color, cmd, width=11).grid(row=0, column=i, padx=6)

        table_frame = tk.Frame(self.tab_expenses, bg="white")
        table_frame.pack(fill="both", expand=True)
        cols = ("Date", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col, w in zip(cols, (110, 140, 110, 400)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure("odd", background="#f6f7fc")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def read_form(self):
        """Validate the form. Returns (iso_date, category, amount, description) or None."""
        date_text = self.date_var.get().strip()
        category = self.cat_var.get().strip()
        amount_text = self.amount_var.get().strip()
        description = self.desc_var.get().strip()
        try:
            iso_date = datetime.strptime(date_text, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Enter the date as DD-MM-YYYY, e.g. 02-10-2026")
            return None
        if not category:
            messagebox.showerror("Missing category", "Please choose or type a category.")
            return None
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a number greater than 0.")
            return None
        return iso_date, category, amount, description

    def add_expense(self):
        data = self.read_form()
        if data is None:
            return
        database.add_expense(self.username, *data)
        self.refresh_all(show_popup=True)

    def update_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("Select a row", "Click an expense in the table first.")
            return
        data = self.read_form()
        if data is None:
            return
        database.update_expense(self.selected_id, *data)
        self.refresh_all(show_popup=True)

    def delete_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("Select a row", "Click an expense in the table first.")
            return
        if messagebox.askyesno("Confirm", "Delete the selected expense?"):
            database.delete_expense(self.selected_id)
            self.refresh_all()

    def refresh_all(self, show_popup=False):
        """Reload table, top cards and analysis after any change."""
        self.clear_form()
        self.load_expenses()
        self.show_analysis(show_popup)

    def clear_form(self):
        self.selected_id = None
        self.date_var.set(datetime.now().strftime("%d-%m-%Y"))
        self.cat_var.set("")
        self.amount_var.set("")
        self.desc_var.set("")

    def load_expenses(self):
        self.tree.delete(*self.tree.get_children())
        for i, (exp_id, date, category, amount, desc) in enumerate(
                database.get_all_expenses(self.username)):
            show_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
            self.tree.insert("", "end", iid=str(exp_id), tags=("odd",) if i % 2 else (),
                             values=(show_date, category, f"{amount:.2f}", desc))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        self.selected_id = int(selection[0])
        date, category, amount, desc = self.tree.item(selection[0])["values"]
        self.date_var.set(str(date))
        self.cat_var.set(str(category))
        self.amount_var.set(str(amount))
        self.desc_var.set(str(desc))

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            initialfile="expenses.csv")
        if not path:
            return
        try:
            count = reports.export_csv(self.username, path)
            messagebox.showinfo("Exported", f"{count} expenses saved to:\n{path}")
        except OSError as error:
            messagebox.showerror("Error", f"Could not save file:\n{error}")

    # ------------------------------------------------ ANALYSIS TAB
    def build_analysis_tab(self):
        now = datetime.now()
        top = tk.Frame(self.tab_analysis, bg="white")
        top.pack(fill="x", pady=(10, 8))
        self.month_var = tk.StringVar(value=reports.MONTHS[now.month])
        self.year_var = tk.StringVar(value=str(now.year))
        tk.Label(top, text="Month", bg="white", fg=GRAY).grid(row=0, column=0, padx=(14, 4), pady=14)
        month_box = ttk.Combobox(top, textvariable=self.month_var, values=reports.MONTHS[1:],
                                 state="readonly", width=12)
        month_box.grid(row=0, column=1)
        month_box.bind("<<ComboboxSelected>>", lambda event: self.show_analysis())
        tk.Label(top, text="Year", bg="white", fg=GRAY).grid(row=0, column=2, padx=(14, 4))
        ttk.Spinbox(top, from_=2000, to=2100, textvariable=self.year_var,
                    width=7).grid(row=0, column=3)
        make_button(top, "Show Analysis", PRIMARY, self.show_analysis, 13).grid(row=0, column=4, padx=(18, 6))
        make_button(top, "Pie Chart", GREEN, self.show_pie, 11).grid(row=0, column=5, padx=6)
        make_button(top, "Bar Graph", ORANGE, self.show_bar, 11).grid(row=0, column=6, padx=6)

        stats = tk.Frame(self.tab_analysis, bg=BG)
        stats.pack(fill="x", pady=4)
        s1, self.a_total = stat_card(stats, "Total Expenses", PRIMARY)
        s2, self.a_count = stat_card(stats, "No. of Entries", GREEN)
        s3, self.a_high = stat_card(stats, "Highest Expense", RED)
        for card in (s1, s2, s3):
            card.pack(side="left", expand=True, fill="x", padx=(0, 8))

        cols = ("Category", "Amount", "Share", "Graph")
        self.breakdown = ttk.Treeview(self.tab_analysis, columns=cols, show="headings", height=5)
        for col, w in zip(cols, (150, 130, 80, 360)):
            self.breakdown.heading(col, text=col)
            self.breakdown.column(col, width=w, anchor="center")
        self.breakdown.pack(fill="x", pady=8)

        budget = tk.Frame(self.tab_analysis, bg="white")
        budget.pack(fill="x", pady=(0, 5))
        self.budget_var = tk.StringVar()
        current = database.get_budget(self.username)
        if current:
            self.budget_var.set(f"{current:.0f}")
        tk.Label(budget, text="Monthly Budget (₹)", bg="white", fg=GRAY).grid(
            row=0, column=0, padx=14, pady=12)
        ttk.Entry(budget, textvariable=self.budget_var, width=14).grid(row=0, column=1)
        make_button(budget, "Set Budget", PRIMARY, self.save_budget, 12).grid(row=0, column=2, padx=12)
        self.bar = ttk.Progressbar(budget, length=330, maximum=100,
                                   style="green.Horizontal.TProgressbar")
        self.bar.grid(row=0, column=3, padx=10)
        self.budget_label = tk.Label(budget, text="", bg="white", font=(FONT, 10, "bold"))
        self.budget_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 10))

    def get_month_year(self):
        try:
            return reports.MONTHS.index(self.month_var.get()), int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please choose a month and enter a valid year.")
            return None

    def show_analysis(self, show_popup=False):
        my = self.get_month_year()
        if my is None:
            return
        self.view_month, self.view_year = my
        self.update_budget_status(show_popup)      # top cards follow the chosen month
        self.breakdown.delete(*self.breakdown.get_children())
        summary = reports.monthly_summary(self.username, *my)
        if summary is None:
            for label in (self.a_total, self.a_count, self.a_high):
                label.config(text="-")
            return
        self.a_total.config(text=f"₹ {summary['total']:,.2f}")
        self.a_count.config(text=str(summary["count"]))
        self.a_high.config(text=f"₹ {summary['highest_amount']:,.0f} ({summary['highest_category']})")
        for category, amount in summary["by_category"].items():
            percent = amount / summary["total"] * 100
            self.breakdown.insert("", "end", values=(category, f"₹ {amount:,.2f}",
                                                     f"{percent:.1f}%", "█" * int(percent / 4)))

    def show_pie(self):
        my = self.get_month_year()
        if my and not charts.pie_chart(self.username, *my):
            messagebox.showinfo("No data", "No expenses found for this month.")

    def show_bar(self):
        my = self.get_month_year()
        if my and not charts.bar_chart(self.username, *my):
            messagebox.showinfo("No data", "No expenses found for this month.")

    # ------------------------------------------------ BUDGET
    def save_budget(self):
        try:
            value = float(self.budget_var.get())
            if value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid budget", "Enter a number greater than 0.")
            return
        database.set_budget(self.username, value)
        self.update_budget_status()
        messagebox.showinfo("Saved", f"Monthly budget set to ₹ {value:.2f}")

    def update_budget_status(self, show_popup=False):
        budget = database.get_budget(self.username)
        spent = reports.month_total(self.username, self.view_month, self.view_year)
        name = f"{reports.MONTHS[self.view_month]} {self.view_year}"
        self.spent_title.config(text=f"Spent in {name}")
        self.left_title.config(text=f"Remaining for {name}")
        self.spent_val.config(text=f"₹ {spent:,.2f}")
        if budget is None:
            self.budget_val.config(text="Not set")
            self.left_val.config(text="-", fg=GRAY)
            self.bar["value"] = 0
            self.budget_label.config(text="No budget set yet.", fg=GRAY)
            return
        self.budget_val.config(text=f"₹ {budget:,.2f}")
        self.bar["value"] = min(spent / budget * 100, 100)
        if spent > budget:
            self.left_val.config(text=f"- ₹ {spent - budget:,.2f}", fg=RED)
            self.bar.config(style="red.Horizontal.TProgressbar")
            self.budget_label.config(text="⚠ Budget Exceeded!", fg=RED)
            if show_popup:
                messagebox.showwarning("Budget Exceeded!",
                                       f"Budget: ₹ {budget:.2f}\nSpent: ₹ {spent:.2f}")
        else:
            self.left_val.config(text=f"₹ {budget - spent:,.2f}", fg=GREEN)
            self.bar.config(style="green.Horizontal.TProgressbar")
            self.budget_label.config(
                text=f"✔ {spent / budget * 100:.0f}% of budget used", fg=GREEN)


if __name__ == "__main__":
    database.create_tables()
    login = LoginWindow()
    login.mainloop()
    if login.success:
        ExpenseApp(login.username).mainloop()