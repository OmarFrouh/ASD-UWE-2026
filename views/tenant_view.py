# Student Name: Feras Bader
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk
from tenant_manager import TenantManager

class TenantView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
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

        self.build_register_tab()
        self.build_list_tab()
        self.build_actions_tab()

    def build_register_tab(self):
        form = ctk.CTkScrollableFrame(self.tab_register)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        fields = [
            ("NI Number:", "ni"), ("Full Name:", "name"), ("Phone:", "phone"),
            ("Email:", "email"), ("Occupation:", "occupation"),
            ("References:", "refs"), ("Emergency Contact:", "emergency"),
            ("Apartment Requirements:", "apt_req"),
            ("Lease Period (months):", "lease_period"),
            ("Username (login):", "username"), ("Password:", "password"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(form, text=label).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            show = "•" if key == "password" else ""
            entry = ctk.CTkEntry(form, width=300, show=show)
            entry.grid(row=i, column=1, padx=10, pady=6)
            self.entries[key] = entry

        ctk.CTkButton(form, text="Register Tenant", command=self.register_tenant, width=300).grid(
            row=len(fields), column=0, columnspan=2, pady=20)

    def build_list_tab(self):
        cols = ("ID", "NI", "Name", "Phone", "Email", "Apt", "Rent", "Status")
        self.tree = ttk.Treeview(self.tab_list, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_list()

    def build_actions_tab(self):
        frame = ctk.CTkFrame(self.tab_actions)
        frame.pack(pady=30, padx=40)

        ctk.CTkLabel(frame, text="Tenant ID:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.action_id_entry = ctk.CTkEntry(frame, width=200)
        self.action_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(frame, text="Early Termination (5% Penalty)", command=self.do_early_termination,
                       width=280, fg_color="orange", hover_color="darkorange").grid(row=1, column=0, columnspan=2, pady=10)

        ctk.CTkButton(frame, text="Archive Tenant", command=self.do_archive,
                       width=280, fg_color="red", hover_color="darkred").grid(row=2, column=0, columnspan=2, pady=10)

        self.action_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.action_result.grid(row=3, column=0, columnspan=2, pady=10)

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
