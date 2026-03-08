import tkinter as tk
from database_manager import DatabaseManager
from auth_manager import AuthManager
from views.main_view import MainView
from views.login_view import LoginView
import sys

def main():
    try:
        # 1. Initialize Backend
        db_name = "pams.db"
        db_manager = DatabaseManager(db_name)
        auth_manager = AuthManager(db_manager)
        from property_manager import PropertyManager
        property_manager = PropertyManager(db_manager)
        
        # 2. Setup GUI Root
        root = tk.Tk()
        
        # 3. Define Navigation Logic
        def launch_dashboard(user):
            # Close the Login Window (which was the root)
            # Actually, since LoginView used 'root', destroying it kills the app.
            # Strategy: LoginView uses a Toplevel or Frame? 
            # Or simpler: Clear the root frame and build Dashboard?
            
            # Better Strategy:
            # 1. Clear all widgets from root (Login View stuff)
            for widget in root.winfo_children():
                widget.destroy()
                
            # 2. Build Main View on the same root
            MainView(root, auth_manager, property_manager, user)

        # 4. Inject Dependencies & Start
        # Pass the callback to LoginView
        app = LoginView(root, auth_manager, launch_dashboard)
        
        print("Starting PAMS...")
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
