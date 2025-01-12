import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Database setup
def setup_database():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add transaction to the database
def add_transaction(description, amount, category, date):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (description, amount, category, date) VALUES (?, ?, ?, ?)",
                   (description, amount, category, date))
    conn.commit()
    conn.close()

# Delete transaction from the database
def delete_transaction(transaction_id):
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()

# Fetch all transactions from the database
def fetch_transactions():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Calculate total balance
def calculate_balance():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions")
    total_balance = cursor.fetchone()[0] or 0
    conn.close()
    return total_balance

# Export to CSV
def export_to_csv():
    transactions = fetch_transactions()
    df = pd.DataFrame(transactions, columns=["ID", "Description", "Amount", "Category", "Date"])
    df.to_csv("transactions.csv", index=False)
    messagebox.showinfo("Export", "Transactions exported to transactions.csv")

# Export to Excel
def export_to_excel():
    transactions = fetch_transactions()
    df = pd.DataFrame(transactions, columns=["ID", "Description", "Amount", "Category", "Date"])
    df.to_excel("transactions.xlsx", index=False)
    messagebox.showinfo("Export", "Transactions exported to transactions.xlsx")

# Export to PDF
def export_to_pdf():
    transactions = fetch_transactions()
    pdf = canvas.Canvas("transactions.pdf", pagesize=letter)
    pdf.setFont("Helvetica", 10)

    y_position = 750  # Initial Y position for the first line

    pdf.drawString(100, y_position, "ID    Description    Amount    Category    Date")
    y_position -= 20  # Move to the next line

    for transaction in transactions:
        transaction_str = f"{transaction[0]}    {transaction[1]}    {transaction[2]}    {transaction[3]}    {transaction[4]}"
        pdf.drawString(100, y_position, transaction_str)
        y_position -= 20
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 750

    pdf.save()
    messagebox.showinfo("Export", "Transactions exported to transactions.pdf")

# GUI setup
class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")

        # Center window on screen
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Title
        self.title_label = tk.Label(root, text="Finance Tracker", font=("Arial", 20))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")

        # Description
        self.description_label = tk.Label(root, text="Description:")
        self.description_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.description_entry = tk.Entry(root, width=30)
        self.description_entry.grid(row=1, column=1, padx=10, pady=5)

        # Amount
        self.amount_label = tk.Label(root, text="Amount:")
        self.amount_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(root, width=30)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5)

        # Category
        self.category_label = tk.Label(root, text="Category:")
        self.category_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.category_entry = tk.Entry(root, width=30)
        self.category_entry.grid(row=3, column=1, padx=10, pady=5)

        # Date
        self.date_label = tk.Label(root, text="Select Date:")
        self.date_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Calendar widget for date selection
        self.calendar = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=4, column=1, padx=10, pady=5)

        # Add Transaction Button
        self.add_button = tk.Button(root, text="Add Transaction", command=self.add_transaction)
        self.add_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")

        # Delete Transaction Button
        self.delete_button = tk.Button(root, text="Delete Selected", command=self.delete_selected)
        self.delete_button.grid(row=5, column=2, padx=10, pady=10, sticky="nsew")

        # Export Buttons
        self.export_csv_button = tk.Button(root, text="Export to CSV", command=export_to_csv)
        self.export_csv_button.grid(row=6, column=0, pady=10, sticky="nsew")

        self.export_excel_button = tk.Button(root, text="Export to Excel", command=export_to_excel)
        self.export_excel_button.grid(row=6, column=1, pady=10, sticky="nsew")

        self.export_pdf_button = tk.Button(root, text="Export to PDF", command=export_to_pdf)
        self.export_pdf_button.grid(row=6, column=2, pady=10, sticky="nsew")

        # Balance Label
        self.balance_label = tk.Label(root, text="Balance: $0.00", font=("Arial", 12))
        self.balance_label.grid(row=7, column=0, columnspan=2, pady=10, sticky="nsew")

        # Transaction List with Checkboxes for Deleting
        self.transaction_tree = ttk.Treeview(root, columns=("ID", "Description", "Amount", "Category", "Date"), show="headings", selectmode="extended")
        self.transaction_tree.heading("ID", text="ID")
        self.transaction_tree.heading("Description", text="Description")
        self.transaction_tree.heading("Amount", text="Amount")
        self.transaction_tree.heading("Category", text="Category")
        self.transaction_tree.heading("Date", text="Date")
        self.transaction_tree.column("ID", width=30)
        self.transaction_tree.column("Description", width=150)
        self.transaction_tree.column("Amount", width=100)
        self.transaction_tree.column("Category", width=100)
        self.transaction_tree.column("Date", width=100)
        self.transaction_tree.grid(row=8, column=0, columnspan=3, pady=10, sticky="nsew")

        # Developer Credit (always visible)
        self.credit_label = tk.Label(root, text="Developed by Ripon R. Rahman", font=("Arial", 10, "italic"))
        self.credit_label.grid(row=9, column=0, columnspan=3, pady=10, sticky="s")

        # Configure grid weight to make sure the window expands properly
        root.grid_rowconfigure(0, weight=0)  # Title
        root.grid_rowconfigure(1, weight=0)  # Description
        root.grid_rowconfigure(2, weight=0)  # Amount
        root.grid_rowconfigure(3, weight=0)  # Category
        root.grid_rowconfigure(4, weight=0)  # Date
        root.grid_rowconfigure(5, weight=0)  # Buttons (Add, Delete)
        root.grid_rowconfigure(6, weight=0)  # Export Buttons
        root.grid_rowconfigure(7, weight=0)  # Balance
        root.grid_rowconfigure(8, weight=1)  # Transaction List
        root.grid_rowconfigure(9, weight=0)  # Developer Name (Always visible)

    def add_transaction(self):
        description = self.description_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.calendar.get_date()

        if not description or not amount or not category or not date:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number!")
            return

        add_transaction(description, amount, category, date)
        self.load_transactions()
        self.update_balance()
        self.clear_entries()

    def delete_selected(self):
        selected_items = self.transaction_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No transactions selected!")
            return

        for item in selected_items:
            transaction_id = self.transaction_tree.item(item, "values")[0]
            delete_transaction(transaction_id)

        self.load_transactions()
        self.update_balance()

    def load_transactions(self):
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        transactions = fetch_transactions()
        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=(transaction[0], transaction[1], transaction[2], transaction[3], transaction[4]))

    def update_balance(self):
        balance = calculate_balance()
        self.balance_label.config(text=f"Balance: ${balance:.2f}")

    def clear_entries(self):
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.calendar.selection_clear()

# Main
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
