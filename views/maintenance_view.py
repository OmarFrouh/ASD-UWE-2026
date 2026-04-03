# Student Name: Numair
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk
from maintenance_manager import MaintenanceManager

class MaintenanceView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.manager = MaintenanceManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="🔧 Maintenance Management", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_new = self.tabview.add("New Ticket")
        tab_list = self.tabview.add("All Tickets")
        tab_manage = self.tabview.add("Manage")

        self.build_new_tab(tab_new)
        self.build_list_tab(tab_list)
        self.build_manage_tab(tab_manage)

    def build_new_tab(self, tab):
        form = ctk.CTkFrame(tab)
        form.pack(pady=20, padx=40)

        ctk.CTkLabel(form, text="Apartment ID:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.apt_id_entry = ctk.CTkEntry(form, width=250)
        self.apt_id_entry.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(form, text="Tenant ID (optional):").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.tenant_id_entry = ctk.CTkEntry(form, width=250)
        self.tenant_id_entry.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkLabel(form, text="Description:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.desc_entry = ctk.CTkEntry(form, width=250)
        self.desc_entry.grid(row=2, column=1, padx=10, pady=8)

        ctk.CTkLabel(form, text="Priority:").grid(row=3, column=0, padx=10, pady=8, sticky="e")
        self.priority_combo = ctk.CTkComboBox(form, values=["Low", "Medium", "High", "Urgent"], width=250)
        self.priority_combo.grid(row=3, column=1, padx=10, pady=8)
        self.priority_combo.set("Medium")

        ctk.CTkButton(form, text="Submit Ticket", command=self.submit_ticket, width=250).grid(
            row=4, column=0, columnspan=2, pady=20)

    def build_list_tab(self, tab):
        # Treeview with vertical scrollbar
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Unit", "Tenant", "Issue", "Priority", "Status", "Reported", "Assigned To")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ctk.CTkButton(tab, text="Refresh", command=self.refresh_list).pack(pady=5)
        self.refresh_list()

    def build_manage_tab(self, tab):
        # ✅ UI BUG FIX: wrap in CTkScrollableFrame so all 13 rows are reachable
        scroll = ctk.CTkScrollableFrame(tab)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="Ticket ID:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.manage_id = ctk.CTkEntry(scroll, width=200)
        self.manage_id.grid(row=0, column=1, padx=10, pady=8)

        # Assign Staff
        ctk.CTkLabel(scroll, text="── Assign Staff ──", font=("Arial", 13, "bold")).grid(row=1, column=0, columnspan=2, pady=(15, 5))

        ctk.CTkLabel(scroll, text="Staff User ID:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.staff_id_entry = ctk.CTkEntry(scroll, width=200)
        self.staff_id_entry.grid(row=2, column=1, padx=10, pady=8)

        ctk.CTkLabel(scroll, text="Scheduled Date:").grid(row=3, column=0, padx=10, pady=8, sticky="e")
        self.sched_entry = ctk.CTkEntry(scroll, width=200, placeholder_text="YYYY-MM-DD")
        self.sched_entry.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkButton(scroll, text="Assign", command=self.assign, width=200).grid(row=4, column=0, columnspan=2, pady=8)

        # Update Status
        ctk.CTkLabel(scroll, text="── Update Status ──", font=("Arial", 13, "bold")).grid(row=5, column=0, columnspan=2, pady=(15, 5))

        self.status_combo = ctk.CTkComboBox(scroll, values=["Open", "Assigned", "In Progress", "Fixed", "Closed"], width=200)
        self.status_combo.grid(row=6, column=0, columnspan=2, pady=8)
        self.status_combo.set("In Progress")

        ctk.CTkButton(scroll, text="Update Status", command=self.update_status, width=200).grid(row=7, column=0, columnspan=2, pady=8)

        # Log Costs
        ctk.CTkLabel(scroll, text="── Log Costs ──", font=("Arial", 13, "bold")).grid(row=8, column=0, columnspan=2, pady=(15, 5))

        ctk.CTkLabel(scroll, text="Hours Spent:").grid(row=9, column=0, padx=10, pady=8, sticky="e")
        self.hours_entry = ctk.CTkEntry(scroll, width=200)
        self.hours_entry.grid(row=9, column=1, padx=10, pady=8)

        ctk.CTkLabel(scroll, text="Cost (£):").grid(row=10, column=0, padx=10, pady=8, sticky="e")
        self.cost_entry = ctk.CTkEntry(scroll, width=200)
        self.cost_entry.grid(row=10, column=1, padx=10, pady=8)

        ctk.CTkButton(scroll, text="Log Costs", command=self.log_costs, width=200).grid(row=11, column=0, columnspan=2, pady=15)

        self.manage_result = ctk.CTkLabel(scroll, text="", font=("Arial", 12))
        self.manage_result.grid(row=12, column=0, columnspan=2, pady=5)

    def submit_ticket(self):
        apt_id = self.apt_id_entry.get()
        tid = self.tenant_id_entry.get()
        desc = self.desc_entry.get()
        priority = self.priority_combo.get()

        if not apt_id or not desc:
            messagebox.showwarning("Error", "Apartment ID and description required.")
            return
        try:
            self.manager.create_ticket(int(apt_id), int(tid) if tid else None, desc, priority)
            messagebox.showinfo("Success", "Ticket created!")
            # ✅ UI BUG FIX: clear all form fields after success, not just description
            for e in [self.apt_id_entry, self.tenant_id_entry, self.desc_entry]:
                e.delete(0, 'end')
            self.priority_combo.set("Medium")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def assign(self):
        tid = self.manage_id.get()
        sid = self.staff_id_entry.get()
        sched = self.sched_entry.get()
        if not tid or not sid:
            messagebox.showwarning("Error", "Ticket ID and Staff ID required.")
            return
        try:
            self.manager.assign_staff(int(tid), int(sid), sched or None)
            self.manage_result.configure(text="Staff assigned!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_status(self):
        tid = self.manage_id.get()
        if not tid:
            messagebox.showwarning("Error", "Enter ticket ID.")
            return
        try:
            self.manager.update_status(int(tid), self.status_combo.get())
            self.manage_result.configure(text="Status updated!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def log_costs(self):
        tid = self.manage_id.get()
        hours = self.hours_entry.get()
        cost = self.cost_entry.get()
        if not tid or not hours or not cost:
            messagebox.showwarning("Error", "All fields required.")
            return
        try:
            self.manager.log_costs(int(tid), hours, cost)
            self.manage_result.configure(text="Costs logged!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.manager.get_all_tickets():
            # id, unit, tenant, desc, priority, status, reported, scheduled, assigned_to, time, cost
            self.tree.insert("", "end", values=(t[0], t[1] or "N/A", t[2] or "N/A",
                (t[3] or "")[:30], t[4], t[5], t[6], t[8] or "Unassigned"))
