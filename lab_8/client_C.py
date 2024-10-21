import tkinter as tk
from tkinter import ttk
import requests

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Transfer Application")
        self.root.geometry("400x300")
        self.create_login_window()

    def create_login_window(self):
        self.login_frame = ttk.Frame(self.root, padding="10")
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.login_frame, text="Username").grid(row=0, column=0, sticky=tk.W)
        self.entry_username = ttk.Entry(self.login_frame)
        self.entry_username.grid(row=0, column=1, pady=5)

        ttk.Label(self.login_frame, text="Password").grid(row=1, column=0, sticky=tk.W)
        self.entry_password = ttk.Entry(self.login_frame, show='*')
        self.entry_password.grid(row=1, column=1, pady=5)

        self.button_login = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.button_login.grid(row=2, columnspan=2, pady=10)

        self.label_status = ttk.Label(self.login_frame, text="", foreground="red")
        self.label_status.grid(row=3, columnspan=2)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        response = requests.post('http://192.168.198.1:5003/login', json={'username': username, 'password': password})

        if response.status_code == 200:
            self.balance = response.json()['balance']
            self.create_transfer_window(username)
        else:
            self.label_status.config(text="Invalid credentials")

    def create_transfer_window(self, username):
        self.login_frame.pack_forget()  # Ẩn cửa sổ đăng nhập

        self.transfer_frame = ttk.Frame(self.root, padding="10")
        self.transfer_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.transfer_frame, text=f"Logged in as: {username}", font=("Helvetica", 14)).grid(row=0, columnspan=2, pady=5)
        ttk.Label(self.transfer_frame, text=f"Balance: {self.balance}", font=("Helvetica", 12)).grid(row=1, columnspan=2, pady=5)

        ttk.Label(self.transfer_frame, text="Transfer To").grid(row=2, column=0, sticky=tk.W)
        self.entry_transfer_to = ttk.Entry(self.transfer_frame)
        self.entry_transfer_to.grid(row=2, column=1, pady=5)

        ttk.Label(self.transfer_frame, text="Amount").grid(row=3, column=0, sticky=tk.W)
        self.entry_amount = ttk.Entry(self.transfer_frame)
        self.entry_amount.grid(row=3, column=1, pady=5)

        self.button_transfer = ttk.Button(self.transfer_frame, text="Transfer", command=lambda: self.transfer(username))
        self.button_transfer.grid(row=4, columnspan=2, pady=10)

        self.label_transfer_status = ttk.Label(self.transfer_frame, text="", foreground="green")
        self.label_transfer_status.grid(row=5, columnspan=2)

        # Khung thông báo chuyển tiền
        self.info_frame = ttk.Frame(self.transfer_frame, padding="5")
        self.info_frame.grid(row=6, columnspan=2, pady=10, sticky=tk.W)
        self.label_transfer_info = ttk.Label(self.info_frame, text="", wraplength=350)
        self.label_transfer_info.pack()

    def transfer(self, username):
        recipient = self.entry_transfer_to.get()
        amount = float(self.entry_amount.get())

        response = requests.post('http://192.168.198.1:5003/transfer',
                                 json={'sender': username, 'recipient': recipient, 'amount': amount})

        if response.status_code == 200 and response.content:
            try:
                message = response.json().get('message', '')
            except ValueError:
                message = 'Invalid JSON response'
        else:
            message = 'Transfer failed'

        if response.status_code == 200:
            self.balance -= amount  # Update balance after transfer
            self.label_transfer_status.config(text=message)
            self.label_transfer_info.config(text=f"Transferred {amount} to {recipient}. New balance: {self.balance}")
        else:
            self.label_transfer_status.config(text=message)
            self.label_transfer_info.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()