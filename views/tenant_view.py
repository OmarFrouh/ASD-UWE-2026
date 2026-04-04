# Student Name: Feras Bader
# Student ID: 24033513

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
        self.tab_archived = self.tabview.add("Archived / Terminated")
        self.tab_actions = self.tabview.add("Actions")
        if self.role == "admin":
            self.tab_assign = self.tabview.add("Assign Apartment")

        self.build_register_tab()
        self.build_list_tab()
        self.build_archived_tab()
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
        # ─── Search & Filter Bar ───
        filter_frame = ctk.CTkFrame(self.tab_list)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="🔍 Search:", font=("Arial", 13)).pack(side="left", padx=(10, 5))
        self.search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="Name, NI, email, phone...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        ctk.CTkLabel(filter_frame, text="Status:", font=("Arial", 13)).pack(side="left", padx=(20, 5))
        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Active", "Archived", "Terminated", "All"],
            width=150,
            command=lambda _: self.refresh_list()
        )
        self.status_filter.pack(side="left", padx=5)
        self.status_filter.set("Active")

        ctk.CTkButton(filter_frame, text="🔄 Reset", width=80,
                       command=self.reset_filters).pack(side="left", padx=10)

        # ─── Summary bar ───
        self.summary_frame = ctk.CTkFrame(self.tab_list)
        self.summary_frame.pack(fill="x", padx=10, pady=5)

        # ─── Data table ───
        tree_frame = ctk.CTkFrame(self.tab_list, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "NI", "Name", "Phone", "Email", "Occupation", "Apt", "Start Date", "End Date", "Rent", "Status")
        self.tree = setup_treeview_scroll(tree_frame, columns=cols, height=15)
        self.refresh_list()

    def build_archived_tab(self):
        tree_frame = ctk.CTkFrame(self.tab_archived, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "NI", "Name", "Status")
        self.archived_tree = setup_treeview_scroll(tree_frame, columns=cols, height=15)

        ctk.CTkButton(self.tab_archived, text="Refresh", command=self.refresh_archived).pack(pady=(5, 10))
        self.refresh_archived()

    def refresh_archived(self):
        for item in self.archived_tree.get_children():
            self.archived_tree.delete(item)
        for t in self.tenant_manager.get_archived_tenants():
            self.archived_tree.insert("", "end", values=(t[0], t[1], t[2], t[3]))

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_filter.set("Active")
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
        try:
            t_id = self.assign_entries["t_id"].get()
            apt_id = self.assign_entries["apt_id"].get()
            start = self.assign_entries["start"].get()
            end = self.assign_entries["end"].get()
            rent = self.assign_entries["rent"].get()
            dep = self.assign_entries["deposit"].get()

            if not all([t_id, apt_id, start, end, rent, dep]):
                raise Exception("All fields are required")

            self.tenant_manager.assign_apartment(
                int(t_id),
                int(apt_id),
                start,
                end,
                float(rent),
                float(dep)
            )
            self.assign_result.configure(text="Apartment Assigned!", text_color="green")
            for e in self.assign_entries.values():
                e.delete(0, 'end')
            self.refresh_list()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for IDs, rent, and deposit.")
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
            messagebox.showwarning("Warning", "Enter Tenant ID")
            return
        
        if not messagebox.askyesno("Confirm Termination", "Are you sure you want to terminate this tenant's lease? This applies a 5% penalty."):
            return
            
        try:
            penalty = self.tenant_manager.early_termination(int(tid))
            messagebox.showinfo("Success", f"Lease terminated. Penalty applied: £{penalty:.2f}")
            self.refresh_list()
        except ValueError:
            messagebox.showerror("Error", "Invalid Tenant ID. Must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_archive(self):
        tid = self.action_id_entry.get()
        if not tid:
            messagebox.showwarning("Warning", "Enter Tenant ID")
            return
            
        if not messagebox.askyesno("Confirm Archive", "Are you sure you want to permanently archive this tenant?"):
            return
            
        try:
            self.tenant_manager.archive_tenant(int(tid))
            messagebox.showinfo("Success", "Tenant Archived.")
            self.refresh_list()
        except ValueError:
            messagebox.showerror("Error", "Invalid Tenant ID. Must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_list(self):
        # Determine data source based on search/filter
        search_query = ""
        if hasattr(self, "search_entry"):
            search_query = self.search_entry.get().strip()

        status = "Active"
        if hasattr(self, "status_filter"):
            status = self.status_filter.get()

        if search_query:
            tenants = self.tenant_manager.search_tenants(search_query)
        else:
            tenants = self.tenant_manager.filter_tenants_by_status(status)

        # Update summary bar
        if hasattr(self, "summary_frame"):
            for w in self.summary_frame.winfo_children():
                w.destroy()
            counts = self.tenant_manager.get_tenant_count_by_status()
            for i, (st, count) in enumerate(counts.items()):
                lbl = ctk.CTkLabel(self.summary_frame,
                    text=f"{st}: {count}",
                    font=("Arial", 12, "bold"),
                    text_color="green" if st == "Active" else "gray")
                lbl.pack(side="left", padx=15, pady=5)

        # Update tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in tenants:
            # user_id, ni, name, phone, email, occupation, apt_id, lease_start, lease_end, rent, status, unit
            self.tree.insert("", "end", values=(
                t[0], t[1], t[2], t[3], t[4], t[5] or "N/A",
                t[11] or "N/A", t[7] or "N/A", t[8] or "N/A",
                f"£{t[9] or 0:.2f}", t[10]
            ))
        self.refresh_archived()
