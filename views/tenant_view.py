# Student Name: Feras Bader
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk
from tenant_manager import TenantManager
from views.ui_helpers import setup_treeview_scroll

class TenantView:
    def __init__(self, parent, db_manager, role="front_desk"):
        self.db_manager = db_manager
        self.role = role
        self.tenant_manager = TenantManager(db_manager)

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.frame, text="👤 Tenant Management", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        # Tabs
        self.tabview = ctk.CTkTabview(self.frame)
        self.tabview.pack(fill="both", expand=True)

        self.tab_register = self.tabview.add("Register")
        self.tab_list = self.tabview.add("Active Tenants")
        self.tab_actions = self.tabview.add("Actions")
        if self.role == "admin":
            self.tab_assign = self.tabview.add("Assign Apartment")

        self.build_register_tab()
        self.build_list_tab()
        self.build_actions_tab()
        if self.role == "admin":
            self.build_assign_tab()

    def build_register_tab(self):
        # Use a standard frame so it auto-sizes perfectly without useless scrolling/truncation
        form = ctk.CTkFrame(self.tab_register)
        form.pack(pady=30)

        fields = [
            ("NI Number:", "ni"), ("Full Name:", "name"), ("Phone:", "phone"),
            ("Email:", "email"), ("Occupation:", "occupation"),
            ("References:", "refs"), ("Emergency Contact:", "emergency"),
            ("Apartment Requirements:", "apt_req"),
            ("Username (login):", "username"), ("Password:", "password"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(form, text=label).grid(row=i, column=0, padx=15, pady=6, sticky="e")
            show = "•" if key == "password" else ""
            entry = ctk.CTkEntry(form, width=280, show=show)
            entry.grid(row=i, column=1, padx=15, pady=6, sticky="w")
            self.entries[key] = entry

        ctk.CTkButton(form, text="Register Tenant", command=self.register_tenant, width=300).grid(
            row=len(fields), column=0, columnspan=2, pady=20)

    def build_list_tab(self):
        tree_frame = ctk.CTkFrame(self.tab_list, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "NI", "Name", "Phone", "Email", "Apt", "Rent", "Status")
        self.tree = setup_treeview_scroll(tree_frame, columns=cols, height=15)
        self.refresh_list()

    def build_actions_tab(self):
        frame = ctk.CTkFrame(self.tab_actions)
        frame.pack(pady=40)

        ctk.CTkLabel(frame, text="Tenant ID:", font=("Arial", 14)).grid(row=0, column=0, padx=15, pady=10, sticky="e")
        self.action_id_entry = ctk.CTkEntry(frame, width=200)
        self.action_id_entry.grid(row=0, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkButton(frame, text="Early Termination (5% Penalty)", command=self.do_early_termination,
                       width=280, fg_color="orange", hover_color="darkorange").grid(row=1, column=0, columnspan=2, pady=10)

        # Archive is a Manager/Admin-only action (Use Case Diagram: Archive Tenant → Manager)
        if self.role in ["admin", "manager"]:
            ctk.CTkButton(frame, text="Archive Tenant", command=self.do_archive,
                           width=280, fg_color="red", hover_color="darkred").grid(row=2, column=0, columnspan=2, pady=10)

        self.action_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.action_result.grid(row=3, column=0, columnspan=2, pady=10)

    def build_assign_tab(self):
        frame = ctk.CTkFrame(self.tab_assign)
        frame.pack(pady=30)

        fields = [
            ("Tenant User ID:", "t_id"),
            ("Apartment ID:", "apt_id"),
            ("Lease Start (YYYY-MM-DD):", "start"),
            ("Lease End (YYYY-MM-DD):", "end"),
            ("Monthly Rent (£):", "rent"),
            ("Deposit (£):", "deposit"),
        ]
        self.assign_entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(frame, text=label, font=("Arial", 13)).grid(row=i, column=0, padx=15, pady=8, sticky="e")
            entry = ctk.CTkEntry(frame, width=220)
            entry.grid(row=i, column=1, padx=15, pady=8, sticky="w")
            self.assign_entries[key] = entry

        self.assign_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.assign_result.grid(row=len(fields), column=0, columnspan=2, pady=5)

        ctk.CTkButton(frame, text="Assign Apartment", command=self.do_assign, width=280).grid(
            row=len(fields) + 1, column=0, columnspan=2, pady=12)

    def do_assign(self):
        v = {k: e.get() for k, e in self.assign_entries.items()}
        if not all([v["t_id"], v["apt_id"], v["start"], v["end"], v["rent"], v["deposit"]]):
            messagebox.showwarning("Error", "All fields are required.")
            return
        try:
            self.tenant_manager.assign_apartment(
                int(v["t_id"]), int(v["apt_id"]),
                v["start"], v["end"],
                float(v["rent"]), float(v["deposit"])
            )
            self.assign_result.configure(text="Apartment assigned successfully!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def register_tenant(self):
        v = {k: e.get() for k, e in self.entries.items()}
        if not v["ni"] or not v["name"] or not v["username"] or not v["password"]:
            messagebox.showwarning("Error", "NI, Name, Username, Password are required.")
            return
        try:
            self.tenant_manager.register_tenant(
                v["username"], v["password"], v["ni"], v["name"],
                v["phone"], v["email"], v["occupation"], v["refs"],
                v["emergency"], v["apt_req"]
            )
            messagebox.showinfo("Success", f"Tenant '{v['name']}' registered!")
            for e in self.entries.values():
                e.delete(0, 'end')
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_early_termination(self):
        tid = self.action_id_entry.get()
        if not tid:
            messagebox.showwarning("Error", "Enter tenant ID.")
            return
        try:
            penalty = self.tenant_manager.early_termination(int(tid))
            self.action_result.configure(text=f"Terminated. Penalty: £{penalty:.2f}", text_color="orange")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_archive(self):
        tid = self.action_id_entry.get()
        if not tid:
            messagebox.showwarning("Error", "Enter tenant ID.")
            return
        try:
            self.tenant_manager.archive_tenant(int(tid))
            self.action_result.configure(text="Tenant archived.", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.tenant_manager.get_all_tenants():
            # user_id, ni, name, phone, email, occupation, apt_id, lease_start, lease_end, rent, status, unit
            self.tree.insert("", "end", values=(t[0], t[1], t[2], t[3], t[4], t[11] or "N/A", f"£{t[9] or 0:.2f}", t[10]))
