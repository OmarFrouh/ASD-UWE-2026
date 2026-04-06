# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from database_manager import DatabaseManager
from auth_manager import AuthManager
from property_manager import PropertyManager
from views.login_view import LoginView
from views.main_view import MainView
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def main():
    try:
        db_manager = DatabaseManager("pams.db")
        db_manager.create_tables()
        auth_manager = AuthManager(db_manager)
        property_manager = PropertyManager(db_manager)

        root = ctk.CTk()

        def launch_login():
            for widget in root.winfo_children():
                widget.destroy()
            LoginView(root, auth_manager, launch_dashboard)

        def launch_dashboard(user):
            for widget in root.winfo_children():
                widget.destroy()
            MainView(root, auth_manager, property_manager, db_manager, user, launch_login)

        launch_login()

        print("Starting PAMS...")
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
