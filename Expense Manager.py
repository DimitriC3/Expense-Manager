import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import matplotlib.dates as mdates


class ExpenseManager:
    def __init__(self):
        self.expenses = {}
        self.load_expenses()

    def add_expense(self, category, amount, description="", date=None):
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")  # Use today's date if none provided
        entry = (amount, description, date)

        if category in self.expenses:
            self.expenses[category].append(entry)
        else:
            self.expenses[category] = [entry]
        self.save_expenses()

    def get_total_expenses(self):
        return sum(amount for category in self.expenses for amount, description, date in self.expenses[category])

    def show_expenses(self):
        return self.expenses

    def save_expenses(self):
        with open('expenses.json', 'w') as file:
            json.dump(self.expenses, file)

    def load_expenses(self):
        if os.path.exists('expenses.json'):
            with open('expenses.json', 'r') as file:
                self.expenses = json.load(file)

    def delete_expense(self, category, expense_index):
        if category in self.expenses and expense_index < len(self.expenses[category]):
            del self.expenses[category][expense_index]
            if len(self.expenses[category]) == 0:
                del self.expenses[category]  # Remove the category if it's empty
            self.save_expenses()
            return True
        return False

    def reset_expenses(self):
        self.expenses = {}  # Reset the dictionary
        self.save_expenses()  # Save the empty state

    def plot_expenses_over_time(self):
        dates = []
        amounts = []

        for category, items in self.expenses.items():
            for amount, description, date in items:
                dates.append(datetime.strptime(date, "%Y-%m-%d"))
                amounts.append(amount)

        # Sort the dates and corresponding amounts
        dates, amounts = zip(*sorted(zip(dates, amounts)))

        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, marker='o', linestyle='-')
        plt.title('Expenses Over Time')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()  # Rotation
        plt.grid(True)
        plt.tight_layout()
        plt.show()

class ExpenseApp:
    def __init__(self, root):
        self.manager = AnalyticalExpenseManager()
        self.root = root
        root.title("Expense Tracker")

        # Set the window size
        root.geometry("450x300")  # Width x Height

        # Expense Entry
        tk.Label(root, text="Category").grid(row=0, column=0)
        tk.Label(root, text="Amount").grid(row=1)
        tk.Label(root, text="Description").grid(row=2)
        tk.Label(root, text="Date (Y-M-D)").grid(row=3)

        self.category = tk.Entry(root)
        self.amount = tk.Entry(root)
        self.description = tk.Entry(root)
        self.date = tk.Entry(root)

        self.category.grid(row=0, column=1)
        self.amount.grid(row=1, column=1)
        self.description.grid(row=2, column=1)
        self.date.grid(row=3, column=1)

        # Buttons
        tk.Button(root, text="Add Expense", command=self.add_expense).grid(row=4, column=0, pady=4)
        tk.Button(root, text="Show Total", command=self.show_total).grid(row=5, column=1, pady=4)
        tk.Button(root, text="List Expenses", command=self.list_expenses).grid(row=5, column=0, pady=4)
        tk.Button(root, text="Analyze by Category", command=self.analyze_category).grid(row=6, column=0, pady=4)
        tk.Button(root, text="Delete Expense", command=self.delete_expense).grid(row=4, column=1, pady=10, padx=10)
        tk.Button(root, text="Plot Expenses Over Time", command=self.plot_time_series).grid(row=6, column=1, pady=10)
        tk.Button(root, text="Reset All Expenses", command=self.reset_all).grid(row=7, column=0, pady=10)

    def reset_all(self):
        confirm = messagebox.askyesno("Reset", "Are you sure you want to reset all expenses?")
        if confirm:
            self.manager.reset_expenses()
            messagebox.showinfo("Reset", "All expenses have been reset.")

    def plot_time_series(self):
        self.manager.plot_expenses_over_time()

    def delete_expense(self):
        category = simpledialog.askstring("Delete Expense", "Enter category:")
        if category and category in self.manager.expenses:
            expense_index = simpledialog.askinteger("Delete Expense",
                                                    f"Enter the index of expense in {category} (0 to {len(self.manager.expenses[category]) - 1}):")
            if expense_index is not None and self.manager.delete_expense(category, expense_index):
                messagebox.showinfo("Deleted", "Expense Deleted Successfully")
            else:
                messagebox.showwarning("Failed", "Failed to delete the expense. Check the index.")
        else:
            messagebox.showwarning("Failed", "Category not found.")

    def analyze_category(self):
        self.manager.plot_expenses_by_category()

    def add_expense(self):
        category = self.category.get()
        try:
            amount = float(self.amount.get())
            description = self.description.get()
            date = self.date.get()
            self.manager.add_expense(category, amount, description, date)
            messagebox.showinfo("Added", "Expense Added Successfully")
            self.category.delete(0, tk.END)
            self.amount.delete(0, tk.END)
            self.description.delete(0, tk.END)
            self.date.delete(0, tk.END)
        except ValueError:
            messagebox.showwarning("Warning", "Amount should be a number")

    def show_total(self):
        total = self.manager.get_total_expenses()
        messagebox.showinfo("Total Expenses", f"Total: ${total}")

    def list_expenses(self):
        expenses = self.manager.show_expenses()
        expense_str = ""
        for category, items in expenses.items():
            expense_str += f"\nCategory: {category}\n"
            for amount, description, date in items:
                expense_str += f"  Amount: ${amount} - Date: {date} - Description: {description}\n"
        messagebox.showinfo("All Expenses", expense_str)


class AnalyticalExpenseManager(ExpenseManager):
    def analyze_by_category(self):
        category_totals = defaultdict(float)
        for category, items in self.expenses.items():
            for amount, description, date in items:
                category_totals[category] += amount
        return category_totals

    def plot_expenses_by_category(self):
        category_totals = self.analyze_by_category()
        categories = list(category_totals.keys())
        totals = list(category_totals.values())

        plt.figure(figsize=(10, 6))
        plt.bar(categories, totals, color='skyblue')
        plt.title('Expenses by Category')
        plt.xlabel('Category')
        plt.ylabel('Total Expenses')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()



