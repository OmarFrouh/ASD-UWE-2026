import tkinter as tk
from tkinter import messagebox

class LoginView:
    def __init__(self, root, auth_manager, on_login_success):
        self.root = root
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success # Callback function
        self.root.title("PAMS - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Title
        tk.Label(root, text="Paragon Apartment System", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Form Container
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10)
        
        # Username
        tk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        tk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Login Button
        tk.Button(root, text="Login", command=self.handle_login, width=15, bg="#4CAF50").pack(pady=20)
        
        # Status Label (Hidden by default)
        self.status_label = tk.Label(root, text="", fg="red")
        self.status_label.pack()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both fields", fg="orange")
            return

        user = self.auth_manager.login(username, password)
        
        if user:
            self.status_label.config(text="Login Successful!", fg="green")
            # Execute the callback, passing the user object
            self.on_login_success(user)
        else:
            self.status_label.config(text="Invalid Username or Password", fg="red")
