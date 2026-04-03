# Student Name: Numair
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox
from maintenance_manager import MaintenanceManager
from views.ui_helpers import setup_treeview_scroll

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
        form.pack(pady=30)

        ctk.CTkLabel(form, text="Apartment ID:").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.apt_id_entry = ctk.CTkEntry(form, width=250)
        self.apt_id_entry.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Tenant ID (optional):").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.tenant_id_entry = ctk.CTkEntry(form, width=250)
        self.tenant_id_entry.grid(row=1, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Description:").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.desc_entry = ctk.CTkEntry(form, width=250)
        self.desc_entry.grid(row=2, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Priority:").grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.priority_combo = ctk.CTkComboBox(form, values=["Low", "Medium", "High", "Urgent"], width=250)
        self.priority_combo.grid(row=3, column=1, padx=15, pady=8, sticky="w")
        self.priority_combo.set("Medium")

        btn = ctk.CTkButton(form, text="Submit Ticket", command=self.submit_ticket, width=250)
        btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # UX bindings
        def on_enter(e): self.submit_ticket()
        for widget in [self.apt_id_entry, self.tenant_id_entry, self.desc_entry]:
            widget.bind("<Return>", on_enter)

    def build_list_tab(self, tab):
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Unit", "Tenant", "Issue", "Priority", "Status", "Reported", "Assigned To", "Hours", "Cost (£)")
        self.tree = setup_treeview_scroll(tree_frame, columns=cols, height=15)

        ctk.CTkButton(tab, text="Refresh", command=self.refresh_list).pack(pady=5)
        self.refresh_list()

    def build_manage_tab(self, tab):
        # Top section: ID
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(pady=(30, 20))
        ctk.CTkLabel(top_frame, text="Ticket ID:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        self.manage_id = ctk.CTkEntry(top_frame, width=200)
        self.manage_id.pack(side="left", padx=10)

        # Bottom section: 3 horizontal columns side-by-side
        cols_frame = ctk.CTkFrame(tab, fg_color="transparent")
        cols_frame.pack(pady=10, fill="x", padx=60)
        cols_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # ---- COL 1: ASSIGN ----
        col1 = ctk.CTkFrame(cols_frame, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=10, sticky="n")
        ctk.CTkLabel(col1, text="Assign Staff", text_color="#1f6aa5", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        ctk.CTkLabel(col1, text="Staff User ID:").pack(anchor="w")
        self.staff_id_entry = ctk.CTkEntry(col1, width=200)
        self.staff_id_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(col1, text="Scheduled Date:").pack(anchor="w")
        self.sched_entry = ctk.CTkEntry(col1, width=200, placeholder_text="YYYY-MM-DD")
        self.sched_entry.pack(pady=(0, 25))
        
        ctk.CTkButton(col1, text="Assign", command=self.assign, width=200).pack()

        # ---- COL 2: STATUS ----
        col2 = ctk.CTkFrame(cols_frame, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=10, sticky="n")
        ctk.CTkLabel(col2, text="Update Status", text_color="#1f6aa5", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        ctk.CTkLabel(col2, text="New Status:").pack(anchor="w")
        self.status_combo = ctk.CTkComboBox(col2, values=["Open", "Assigned", "In Progress", "Fixed", "Closed"], width=200)
        self.status_combo.pack(pady=(0, 25))
        self.status_combo.set("In Progress")
        
        ctk.CTkButton(col2, text="Update Status", command=self.update_status, width=200).pack()

        # ---- COL 3: COSTS ----
        col3 = ctk.CTkFrame(cols_frame, fg_color="transparent")
        col3.grid(row=0, column=2, padx=20, pady=10, sticky="n")
        ctk.CTkLabel(col3, text="Log Costs", text_color="#1f6aa5", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        ctk.CTkLabel(col3, text="Hours Spent:").pack(anchor="w")
        self.hours_entry = ctk.CTkEntry(col3, width=200)
        self.hours_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(col3, text="Cost (£):").pack(anchor="w")
        self.cost_entry = ctk.CTkEntry(col3, width=200)
        self.cost_entry.pack(pady=(0, 25))
        
        ctk.CTkButton(col3, text="Log Costs", command=self.log_costs, width=200).pack()

        self.manage_result = ctk.CTkLabel(tab, text="", font=("Arial", 12))
        self.manage_result.pack(pady=20)

        
        # Enter key bindings for UX
        self.manage_id.bind("<Return>", lambda e: self.update_status())
        self.hours_entry.bind("<Return>", lambda e: self.log_costs())
        self.cost_entry.bind("<Return>", lambda e: self.log_costs())
        self.staff_id_entry.bind("<Return>", lambda e: self.assign())
        self.sched_entry.bind("<Return>", lambda e: self.assign())

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
        except ValueError:
            messagebox.showerror("Error", "Ticket ID and Staff ID must be valid numbers.")
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
        except ValueError:
            messagebox.showerror("Error", "Ticket ID must be a valid number.")
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
        except ValueError:
            messagebox.showerror("Error", "Ticket ID, Hours, and Cost must be valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.manager.get_all_tickets():
            # id, unit, tenant, desc, priority, status, reported, scheduled, assigned_to, time, cost
            self.tree.insert("", "end", values=(t[0], t[1] or "N/A", t[2] or "N/A",
                (t[3] or "")[:30], t[4], t[5], t[6], t[8] or "Unassigned", 
                f"{t[9] or 0.0:.1f}", f"£{(t[10] or 0.0):.2f}"))
