# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox

class LoginView:
    def __init__(self, root, auth_manager, on_login_success):
        self.root = root
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        self.root.title("PAMS - Login")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        frame = ctk.CTkFrame(root, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🏢 PAMS", font=("Arial", 28, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(frame, text="Paragon Apartment Management", font=("Arial", 13), text_color="gray").pack(pady=(0, 25))

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=8, padx=40)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="•", width=280, height=40)
        self.password_entry.pack(pady=8, padx=40)

        ctk.CTkButton(frame, text="Login", command=self.handle_login, width=280, height=40, font=("Arial", 14, "bold")).pack(pady=20)

        self.status_label = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=(0, 20))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Please enter both fields", text_color="orange")
            return

        user = self.auth_manager.login(username, password)
        if user:
            self.status_label.configure(text="Login Successful!", text_color="green")
            self.on_login_success(user)
        else:
            self.status_label.configure(text="Invalid Username or Password", text_color="red")
