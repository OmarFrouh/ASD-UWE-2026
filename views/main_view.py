# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox

class MainView:
    def __init__(self, root, auth_manager, property_manager, db_manager, current_user, on_logout=None):
        self.root = root
        self.auth_manager = auth_manager
        self.property_manager = property_manager
        self.db_manager = db_manager
        self.current_user = current_user
        self.on_logout = on_logout

        self.root.title("PAMS - Dashboard")
        self.root.geometry("1200x700")

        # Header
        header = ctk.CTkFrame(root, height=50, corner_radius=0)
        header.pack(side="top", fill="x")
        ctk.CTkLabel(header, text="🏢 Paragon Apartment Management System", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text=f"👤 {self.current_user[1]} ({self.current_user[3]})", font=("Arial", 12)).pack(side="right", padx=20)

        # Sidebar
        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.setup_sidebar()

        # Content
        self.content_frame = ctk.CTkFrame(root, corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")
        self.show_view("dashboard")

    def setup_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="Navigation", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        role = self.current_user[3]

        ctk.CTkButton(self.sidebar, text="📊 Dashboard", command=lambda: self.show_view("dashboard"), width=180).pack(pady=4, padx=10)

        if role == "admin":
            ctk.CTkButton(self.sidebar, text="👥 Users", command=lambda: self.show_view("users"), width=180).pack(pady=4, padx=10)

        if role in ["admin"]:
            ctk.CTkButton(self.sidebar, text="🏠 Apartments", command=lambda: self.show_view("apartments"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "front_desk", "manager"]:
            ctk.CTkButton(self.sidebar, text="👤 Tenants", command=lambda: self.show_view("tenants"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "finance_manager"]:
            ctk.CTkButton(self.sidebar, text="💰 Invoices", command=lambda: self.show_view("invoices"), width=180).pack(pady=4, padx=10)
            ctk.CTkButton(self.sidebar, text="💳 Payments", command=lambda: self.show_view("payments"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "front_desk", "maintenance"]:
            ctk.CTkButton(self.sidebar, text="🔧 Maintenance", command=lambda: self.show_view("maintenance"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "manager"]:
            ctk.CTkButton(self.sidebar, text="📈 Reports", command=lambda: self.show_view("reports"), width=180).pack(pady=4, padx=10)

        ctk.CTkButton(self.sidebar, text="🚪 Logout", command=self.logout, width=180, fg_color="red", hover_color="darkred").pack(side="bottom", pady=20, padx=10)

    def check_permissions(self, permission):
        role = self.current_user[3]
        if permission == "manage_users":
            return role == 'admin'
        return False

    def show_view(self, view_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view_name == "dashboard":
            self.show_dashboard()
        elif view_name == "users":
            from views.user_view import UserView
            UserView(self.content_frame, self.auth_manager)
        elif view_name == "apartments":
            from views.apartment_view import ApartmentView
            ApartmentView(self.content_frame, self.property_manager)
        elif view_name == "tenants":
            try:
                from views.tenant_view import TenantView
                TenantView(self.content_frame, self.db_manager, self.current_user[3])
            except ImportError:
                ctk.CTkLabel(self.content_frame, text="👤 Tenants — Coming Soon (Feras)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "invoices":
            try:
                from views.invoice_view import InvoiceView
                InvoiceView(self.content_frame, self.db_manager)
            except ImportError:
                ctk.CTkLabel(self.content_frame, text="💰 Invoices — Coming Soon (Ahmed)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "payments":
            try:
                from views.payment_view import PaymentView
                PaymentView(self.content_frame, self.db_manager)
            except ImportError:
                ctk.CTkLabel(self.content_frame, text="💳 Payments — Coming Soon (Ahmed)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "maintenance":
            try:
                from views.maintenance_view import MaintenanceView
                MaintenanceView(self.content_frame, self.db_manager)
            except ImportError:
                ctk.CTkLabel(self.content_frame, text="🔧 Maintenance — Coming Soon (Numair)", font=("Arial", 20)).pack(pady=50)
        elif view_name == "reports":
            ctk.CTkLabel(self.content_frame, text="📈 Reports — Coming Sprint 2", font=("Arial", 20)).pack(pady=50)

    def show_dashboard(self):
        ctk.CTkLabel(self.content_frame, text="📊 Dashboard", font=("Arial", 24, "bold")).pack(pady=30)
        stats = self.auth_manager.get_dashboard_stats()
        frame = ctk.CTkFrame(self.content_frame)
        frame.pack(pady=20, padx=40, fill="x")
        for i, (key, val) in enumerate(stats.items()):
            card = ctk.CTkFrame(frame, corner_radius=10)
            card.grid(row=0, column=i, padx=15, pady=15, sticky="nsew")
            frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=str(val), font=("Arial", 36, "bold")).pack(pady=(20, 5))
            ctk.CTkLabel(card, text=key, font=("Arial", 13), text_color="gray").pack(pady=(0, 20))

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            if self.on_logout:
                self.on_logout()
            else:
                self.root.destroy()
