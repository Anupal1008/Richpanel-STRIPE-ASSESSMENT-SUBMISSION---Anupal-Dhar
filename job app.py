#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
import stripe
import sqlite3
from tabulate import tabulate
from tkinter import ttk
from tkinter import messagebox


# Set your Stripe API key
stripe.api_key = 'sk_test_51NbU8dSDbyPszWPJRzQfIgnK3DuBbgqn3ROJxHmpkA7MSJrFGog4mV8I9iUuTGuq0hze6srg89FALKWVAEm5vsUV00NEhoiJFA'

class SubscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subscription App")

        self.conn = sqlite3.connect('subscription_db.db')
        self.cursor = self.conn.cursor()

        self.create_plans_table()
        self.create_users_table()
        self.create_login_screen()

    def create_plans_table(self):
        cursor = self.cursor
        cursor.execute("""
            CREATE TABLE plans (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                monthly_price INTEGER NOT NULL,
                yearly_price INTEGER NOT NULL,
                video_quality TEXT NOT NULL,
                resolution TEXT NOT NULL,
                devices TEXT NOT NULL,
                number_of_screens INTEGER NOT NULL,
                stripe_price_id TEXT NOT NULL
            );
        """)
        cursor.executemany("""
            INSERT INTO plans (name, monthly_price, yearly_price, video_quality, resolution, devices, number_of_screens, stripe_price_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            ('Basic', 100, 1000, 'Good', '480p', 'Phone', 1, 'price_100'),
            ('Standard', 200, 2000, 'Good', '720P', 'Phone+Tablet', 3, 'price_200'),
            ('Premium', 500, 5000, 'Better', '1080P', 'Phone+Tablet+Computer', 5, 'price_500'),
            ('Regular', 700, 7000, 'Best', '4K+HDR', 'Phone+Tablet+TV', 10, 'price_700'),
        ])
        self.conn.commit()

        self.plans_data = []
        for plan in self.get_plans():
            monthly_price = None
            if type(plan[2]) == str:  # Assuming monthly_price is at index 2
                monthly_price = int(plan[2])
            else:
                monthly_price = plan[2]






    def create_users_table(self):
        cursor = self.cursor
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def create_login_screen(self):
        
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack()

        self.signup_button = tk.Button(self.login_frame, text="Sign up", command=self.signup)
        self.signup_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please enter your username and password")
            return

        cursor = self.cursor
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user is None:
            messagebox.showerror("Error", "Invalid username or password")
            return

        self.current_user = user
        self.plans_data = self.get_plans()
        self.create_plans_screen()

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please enter your username and password")
            return

        cursor = self.cursor
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user is not None:
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

        messagebox.showinfo("Signup", "You have successfully signed up")
        self.login()

    def create_plans_screen(self):
        self.plans_frame = tk.Frame(self.root)
        self.plans_frame.pack()

        self.plans_label = tk.Label(self.plans_frame, text="Available Plans:")
        self.plans_label.pack()

        self.plans_table = ttk.Treeview(self.plans_frame, columns=("Plan Name", "Monthly Price", "Yearly Price", "Resolution", "Devices"))
        self.plans_table.pack()
        
        # Set the headers of the table
        self.plans_table.column("#0", width=0, stretch=False)
        self.plans_table.column("Plan Name", width=150)
        self.plans_table.column("Monthly Price", width=100)
        self.plans_table.column("Yearly Price", width=100)
        self.plans_table.column("Resolution", width=100)
        self.plans_table.column("Devices", width=100)

        self.plans_data = []
        for plan in self.get_plans():
            monthly_price = int(plan[2])
            quality = plan[4]
            resolution = plan[5]
            devices = plan[6]
            self.plans_data.append([plan[1], monthly_price, plan[3],quality, resolution, devices])

        # Iterate over the plans data and insert each plan into the treeview
        for plan_data in self.plans_data:
            self.plans_table.insert("", "end", values=plan_data)

        self.plan_selection_label = tk.Label(self.plans_frame, text="Select a Plan:")
        self.plan_selection_label.pack()

        self.plan_selection = tk.StringVar()
        self.plan_selection.set("Basic")
        self.plan_selection_menu = ttk.OptionMenu(self.plans_frame, self.plan_selection, *self.plans_data)
        self.plan_selection_menu.pack()

        self.billing_interval_label = tk.Label(self.plans_frame, text="Billing Interval:")
        self.billing_interval_label.pack()

        self.billing_interval_var = tk.StringVar(value="Monthly")
        self.billing_interval_monthly = ttk.Radiobutton(self.plans_frame, text="Monthly", variable=self.billing_interval_var, value="Monthly")
        self.billing_interval_monthly.pack()

        self.billing_interval_yearly = ttk.Radiobutton(self.plans_frame, text="Yearly", variable=self.billing_interval_var, value="Yearly")
        self.billing_interval_yearly.pack()

        self.credit_card_label = tk.Label(self.plans_frame, text="Enter Credit Card Information:")
        self.credit_card_label.pack()

        self.credit_card_entry = tk.Entry(self.plans_frame, show="*")
        self.credit_card_entry.pack()

        self.subscribe_button = tk.Button(self.plans_frame, text="Subscribe", command=self.subscribe)
        self.subscribe_button.pack()

    def subscribe(self):
        plan_name = self.plan_selection.get()
        billing_interval = self.billing_interval_var.get()
        credit_card = self.credit_card_entry.get()

        try:
            customer = stripe.Customer.create(source=credit_card)
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': self.get_plan_details(plan_name)["stripe_price_id"]}],
                billing=billing_interval.lower()
            )

            # Store subscription details in your database
            self.store_subscription_in_database(customer.id, plan_name, billing_interval, subscription.id)

            # Display subscription details
            self.show_subscription_details(plan_name, billing_interval)

        except stripe.error.StripeError as e:
            # Handle Stripe errors
            print(e)

    def get_plans(self):
        cursor = self.cursor
        cursor.execute("SELECT * FROM plans")
        plans = [plan for plan in cursor.fetchall()]
        return plans

    def get_plan_details(self, plan_name):
        cursor = self.cursor
        cursor.execute("SELECT * FROM plans WHERE name=?", (plan_name,))
        plan = cursor.fetchone()
        return plan

    def store_subscription_in_database(self, customer_id, plan_name, billing_interval, subscription_id):
        cursor = self.cursor
        cursor.execute("""
            INSERT INTO subscriptions (customer_id, plan_name, billing_interval, subscription_id)
            VALUES (?, ?, ?, ?);
        """, (customer_id, plan_name, billing_interval, subscription_id))
        self.conn.commit()

    def show_subscription_details(self, plan_name, billing_interval):
        messagebox.showinfo("Subscription Details", "You have successfully subscribed to the {} plan on a {} billing interval.".format(plan_name, billing_interval))

    def mainloop(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriptionApp(root)
    app.mainloop()


# In[ ]:




