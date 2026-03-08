import tkinter as tk
from tkinter import messagebox
# Import views that will be displayed in the content area
# from views.user_view import UserView (Will implement next)

class MainView:
    def __init__(self, root, auth_manager, property_manager, current_user):
        self.root = root
        self.auth_manager = auth_manager
        self.property_manager = property_manager
        self.current_user = current_user
        
        self.root.title("PAMS - Dashboard")
        self.root.geometry("1000x600")
        
        # --- Layout ---
        # 1. Header (Top)
        header_frame = tk.Frame(root, bg="#333", height=50)
        header_frame.pack(side="top", fill="x")
        
        title_label = tk.Label(header_frame, text="Paragon Apartment Management System", bg="#333", fg="white", font=("Arial", 14, "bold"))
        title_label.pack(side="left", padx=20, pady=10)
        
        user_label = tk.Label(header_frame, text=f"User: {self.current_user[1]} ({self.current_user[3]})", bg="#333", fg="#ccc")
        user_label.pack(side="right", padx=20)
        
        # 2. Sidebar (Left)
        self.sidebar_frame = tk.Frame(root, bg="#f0f0f0", width=200)
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.setup_sidebar()

        # 3. Content Area (Center/Right)
        self.content_frame = tk.Frame(root, bg="white")
        self.content_frame.pack(side="right", expand=True, fill="both")
        
        # Initialize Default View
        self.show_view("dashboard")

    def setup_sidebar(self):
        """
        Creates the sidebar buttons based on permissions.
        (Matches Class Diagram: + setup_sidebar())
        """
        # Common Buttons
        tk.Button(self.sidebar_frame, text="Dashboard", command=lambda: self.show_view("dashboard"), width=20, pady=5).pack(pady=5, padx=10)
        
        # Permission Logic (Matches Class Diagram: + check_permissions() logic)
        if self.check_permissions("manage_users"):
            tk.Button(self.sidebar_frame, text="User Management", command=lambda: self.show_view("users"), width=20, pady=5).pack(pady=5, padx=10)
            
        tk.Button(self.sidebar_frame, text="Apartments", command=lambda: self.show_view("apartments"), width=20, pady=5).pack(pady=5, padx=10)
        
        # Spacer & Logout
        tk.Frame(self.sidebar_frame, height=20, bg="#f0f0f0").pack() 
        tk.Button(self.sidebar_frame, text="Logout", command=self.logout, width=20, pady=5, fg="red").pack(side="bottom", pady=20, padx=10)

    def check_permissions(self, permission):
        """
        Checks if the current user has the required permission.
        (Matches Class Diagram: + check_permissions())
        """
        role = self.current_user[3]
        
        if permission == "manage_users":
            return role == 'admin'
        
        return False

    def show_view(self, view_name):
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if view_name == "dashboard":
            tk.Label(self.content_frame, text="Welcome to the Dashboard", font=("Arial", 20)).pack(pady=50)
            tk.Label(self.content_frame, text="Select an option from the sidebar.").pack()
            
        elif view_name == "users":
            from views.user_view import UserView
            UserView(self.content_frame, self.auth_manager)
        elif view_name == "apartments":
             from views.apartment_view import ApartmentView
             ApartmentView(self.content_frame, self.property_manager)

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()
            # In a real cycle, we might callback to main to restart login, 
            # but for now closing the app is a safe 'logout'.
            # Or we can handle rebooting via main.py loop.
