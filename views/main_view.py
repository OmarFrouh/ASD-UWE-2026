# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from tkinter import messagebox
from notification_manager import NotificationManager

class MainView:
    def __init__(self, root, auth_manager, property_manager, db_manager, current_user, on_logout=None):
        self.root = root
        self.auth_manager = auth_manager
        self.property_manager = property_manager
        self.db_manager = db_manager
        self.current_user = current_user
        self.on_logout = on_logout

        self.notification_manager = NotificationManager(db_manager)

        self.root.title("PAMS - Dashboard")
        self.root.resizable(True, True)
        self.root.minsize(900, 580)
        w, h = 1200, 700
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")

        # Header
        header = ctk.CTkFrame(root, height=50, corner_radius=0)
        header.pack(side="top", fill="x")
        ctk.CTkLabel(header, text="🏢 Paragon Apartment Management System", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=10)

        # Profile is packed first to stay on the far right
        ctk.CTkLabel(header, text=f"👤 {self.current_user[1]} ({self.current_user[3]})", font=("Arial", 12)).pack(side="right", padx=10)

        # ─── SPRINT 2 NOTIFICATION BADGE ─── clickable button, not static label
        self.notif_btn = ctk.CTkButton(
            header, text="", font=("Arial", 13, "bold"),
            text_color="white", fg_color="#c0392b", hover_color="#e74c3c",
            command=self.show_notifications, width=160, height=30, corner_radius=6
        )
        self.notif_btn.pack(side="right", padx=(0, 20))
        self.update_notification_badge()

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.setup_sidebar()

        # Content
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")
        self.show_view("dashboard")

    def update_notification_badge(self):
        """Updates the notification badge button in the header."""
        count = self.notification_manager.get_notification_count()
        if count > 0:
            self.notif_btn.configure(text=f"🔔 {count} Notifications")
            self.notif_btn.pack(side="right", padx=(0, 20))
        else:
            self.notif_btn.pack_forget()

    def show_notifications(self):
        """Opens a popup listing all active notifications (overdue invoices + expiring leases)."""
        notifications = self.notification_manager.get_notifications()
        popup = ctk.CTkToplevel(self.root)
        popup.title("Notifications")
        popup.geometry("600x420")
        popup.grab_set()

        ctk.CTkLabel(popup, text="🔔 Active Notifications",
                     font=("Arial", 16, "bold"), text_color="#e74c3c").pack(pady=(16, 8))

        if not notifications:
            ctk.CTkLabel(popup, text="No active notifications.", font=("Arial", 13)).pack(pady=20)
        else:
            for n in notifications:
                row = ctk.CTkFrame(popup, corner_radius=8)
                row.pack(fill="x", padx=16, pady=4)
                ctk.CTkLabel(row, text=n["text"], font=("Arial", 12), anchor="w").pack(
                    fill="x", padx=10, pady=6)

        ctk.CTkButton(popup, text="Close", command=popup.destroy, width=120).pack(pady=14)

    def setup_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="Navigation", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        role = self.current_user[3]

        ctk.CTkButton(self.sidebar, text="📊 Dashboard", command=lambda: self.show_view("dashboard"), width=180).pack(pady=4, padx=10)

        if role == "admin":
            ctk.CTkButton(self.sidebar, text="👥 Users", command=lambda: self.show_view("users"), width=180).pack(pady=4, padx=10)

        if role in ["admin"]:
            ctk.CTkButton(self.sidebar, text="🏠 Apartments", command=lambda: self.show_view("apartments"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "front_desk"]:
            ctk.CTkButton(self.sidebar, text="👤 Tenants", command=lambda: self.show_view("tenants"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "finance_manager"]:
            ctk.CTkButton(self.sidebar, text="💰 Invoices", command=lambda: self.show_view("invoices"), width=180).pack(pady=4, padx=10)
            ctk.CTkButton(self.sidebar, text="💳 Payments", command=lambda: self.show_view("payments"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "maintenance"]:
            ctk.CTkButton(self.sidebar, text="🔧 Maintenance", command=lambda: self.show_view("maintenance"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "manager"]:
            ctk.CTkButton(self.sidebar, text="📈 Reports", command=lambda: self.show_view("reports"), width=180).pack(pady=4, padx=10)

        ctk.CTkButton(self.sidebar, text="🚪 Logout", command=self.logout, width=180, fg_color="red", hover_color="darkred").pack(side="bottom", pady=20, padx=10)

    ROLE_PERMISSIONS = {
        "admin": ["dashboard", "users", "apartments", "tenants", "invoices", "payments", "maintenance", "reports"],
        "front_desk": ["dashboard", "tenants"],
        "finance_manager": ["dashboard", "invoices", "payments"],
        "maintenance": ["dashboard", "maintenance"],
        "manager": ["dashboard", "reports"],
    }

    def show_view(self, view_name):
        role = self.current_user[3]
        allowed = self.ROLE_PERMISSIONS.get(role, ["dashboard"])
        if view_name not in allowed:
            messagebox.showerror("Access Denied", f"Your role ({role}) cannot access {view_name}.")
            return

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
            from views.tenant_view import TenantView
            TenantView(self.content_frame, self.db_manager, self.current_user[3])
        elif view_name == "invoices":
            from views.invoice_view import InvoiceView
            InvoiceView(self.content_frame, self.db_manager)
        elif view_name == "payments":
            from views.payment_view import PaymentView
            PaymentView(self.content_frame, self.db_manager)
        elif view_name == "maintenance":
            from views.maintenance_view import MaintenanceView
            MaintenanceView(self.content_frame, self.db_manager)
        elif view_name == "reports":
            from views.report_view import ReportView
            ReportView(self.content_frame, self.db_manager)

    def show_dashboard(self):
        self.update_notification_badge()
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
