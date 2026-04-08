# Student Name: Feras Bader
# Student ID: 24033513

import customtkinter as ctk
from tkinter import messagebox, ttk
from tenant_manager import TenantManager
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes, enable_trackpad_scroll

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
        self.tab_edit = self.tabview.add("Edit Tenant")
        self.tab_complaints = self.tabview.add("Complaints")
        self.tab_actions = self.tabview.add("Actions")
        if self.role == "admin":
            self.tab_assign = self.tabview.add("Assign Apartment")

        self.build_register_tab()
        self.build_list_tab()
        self.build_archived_tab()
        self.build_edit_tab()
        self.build_complaints_tab()
        self.build_actions_tab()
        if self.role == "admin":
            self.build_assign_tab()

    def build_register_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_register, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        form = ctk.CTkFrame(scroll)
        form.pack(pady=20)

        # Required fields are marked with *
        required_keys = {"ni", "name", "username", "password"}
        fields = [
            ("NI Number *:", "ni"), ("Full Name *:", "name"), ("Phone:", "phone"),
            ("Email:", "email"), ("Occupation:", "occupation"),
            ("References:", "refs"), ("Emergency Contact:", "emergency"),
            ("Apartment Requirements:", "apt_req"),
            ("Username (login) *:", "username"), ("Password *:", "password"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            text_color = "red" if key in required_keys else None
            ctk.CTkLabel(form, text=label, text_color=text_color).grid(row=i, column=0, padx=15, pady=6, sticky="e")
            show = "•" if key == "password" else ""
            entry = ctk.CTkEntry(form, width=280, show=show)
            entry.grid(row=i, column=1, padx=15, pady=6, sticky="w")
            self.entries[key] = entry

        ctk.CTkButton(form, text="Register Tenant", command=self.register_tenant, width=300).grid(
            row=len(fields), column=0, columnspan=2, pady=20)
        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

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
        apply_row_stripes(self.archived_tree)
        autofit_columns(self.archived_tree)

    def build_edit_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_edit, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        frame = ctk.CTkFrame(scroll)
        frame.pack(pady=20)

        # ─── Load Section ───
        ctk.CTkLabel(frame, text="Tenant ID *:", text_color="red").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.edit_id_entry = ctk.CTkEntry(frame, width=200)
        self.edit_id_entry.grid(row=0, column=1, padx=15, pady=8, sticky="w")
        ctk.CTkButton(frame, text="Load Tenant", command=self.load_tenant_for_edit, width=150).grid(
            row=0, column=2, padx=10, pady=8)

        # ─── NI Number (read-only display) ───
        ctk.CTkLabel(frame, text="NI Number:").grid(row=1, column=0, padx=15, pady=6, sticky="e")
        self.edit_ni_label = ctk.CTkLabel(frame, text="—", font=("Arial", 13))
        self.edit_ni_label.grid(row=1, column=1, padx=15, pady=6, sticky="w")

        # ─── Editable Fields ───
        edit_fields = [
            ("Full Name:", "edit_name"),
            ("Phone:", "edit_phone"),
            ("Email:", "edit_email"),
            ("Occupation:", "edit_occupation"),
            ("References:", "edit_refs"),
            ("Emergency Contact:", "edit_emergency"),
            ("Apartment Requirements:", "edit_apt_req"),
        ]
        self.edit_entries = {}
        for i, (label, key) in enumerate(edit_fields, start=2):
            ctk.CTkLabel(frame, text=label).grid(row=i, column=0, padx=15, pady=6, sticky="e")
            entry = ctk.CTkEntry(frame, width=280)
            entry.grid(row=i, column=1, padx=15, pady=6, sticky="w")
            self.edit_entries[key] = entry

        # ─── Lease Info (read-only display) ───
        info_row = len(edit_fields) + 2
        ctk.CTkLabel(frame, text="── Lease Info (read-only) ──", font=("Arial", 11),
                     text_color="gray").grid(row=info_row, column=0, columnspan=3, pady=(10, 5))
        self.edit_lease_label = ctk.CTkLabel(frame, text="Load a tenant to see lease details",
                                              font=("Arial", 12), text_color="gray")
        self.edit_lease_label.grid(row=info_row + 1, column=0, columnspan=3, pady=5)

        # ─── Save Button ───
        ctk.CTkButton(frame, text="Save Changes", command=self.save_tenant_edit, width=280,
                       fg_color="green", hover_color="darkgreen").grid(
            row=info_row + 2, column=0, columnspan=3, pady=15)

        self.edit_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.edit_result.grid(row=info_row + 3, column=0, columnspan=3, pady=5)

        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

    def load_tenant_for_edit(self):
        """Loads tenant data into the edit form."""
        tid = self.edit_id_entry.get()
        if not tid:
            messagebox.showwarning("Missing Field", "Please enter a Tenant ID.")
            return
        try:
            tid_int = int(tid)
        except ValueError:
            messagebox.showerror("Invalid Input", "Tenant ID must be a number.")
            return

        tenant = self.tenant_manager.get_tenant_by_id(tid_int)
        if not tenant:
            messagebox.showerror("Not Found", f"No tenant found with ID {tid_int}.")
            return
        if tenant[14] in ("Terminated", "Archived"):
            messagebox.showerror("Invalid Action", f"Tenant is {tenant[14]} — cannot edit.")
            return

        # Populate NI (read-only)
        self.edit_ni_label.configure(text=tenant[1] or "N/A")

        # Populate editable fields
        # Indices: 2=name, 3=phone, 4=email, 5=occupation, 6=refs, 7=emergency, 8=apt_req
        field_map = {
            "edit_name": tenant[2] or "",
            "edit_phone": tenant[3] or "",
            "edit_email": tenant[4] or "",
            "edit_occupation": tenant[5] or "",
            "edit_refs": tenant[6] or "",
            "edit_emergency": tenant[7] or "",
            "edit_apt_req": tenant[8] or "",
        }
        for key, val in field_map.items():
            self.edit_entries[key].delete(0, "end")
            self.edit_entries[key].insert(0, val)

        # Populate lease info (read-only)
        apt_id = tenant[9]
        lease_start = tenant[10] or "N/A"
        lease_end = tenant[11] or "N/A"
        rent = f"£{tenant[12]:.2f}" if tenant[12] else "N/A"
        deposit = f"£{tenant[13]:.2f}" if tenant[13] else "N/A"
        self.edit_lease_label.configure(
            text=f"Apt: {apt_id or 'None'}  |  Lease: {lease_start} → {lease_end}  |  Rent: {rent}  |  Deposit: {deposit}",
            text_color="white")
        self.edit_result.configure(text=f"Loaded tenant: {tenant[2]}", text_color="cyan")

    def save_tenant_edit(self):
        """Saves edited tenant fields."""
        tid = self.edit_id_entry.get()
        if not tid:
            messagebox.showwarning("Missing Field", "Load a tenant first.")
            return

        try:
            tid_int = int(tid)
            self.tenant_manager.update_tenant(
                tid_int,
                full_name=self.edit_entries["edit_name"].get() or None,
                phone=self.edit_entries["edit_phone"].get() or None,
                email=self.edit_entries["edit_email"].get() or None,
                occupation=self.edit_entries["edit_occupation"].get() or None,
                references=self.edit_entries["edit_refs"].get() or None,
                emergency_contact=self.edit_entries["edit_emergency"].get() or None,
                apt_requirements=self.edit_entries["edit_apt_req"].get() or None,
            )
            messagebox.showinfo("Success", "Tenant updated successfully!")
            self.edit_result.configure(text="Changes saved!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def build_complaints_tab(self):
        # ─── Log New Complaint ───
        log_frame = ctk.CTkFrame(self.tab_complaints)
        log_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(log_frame, text="📋 Log New Complaint", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 5))

        ctk.CTkLabel(log_frame, text="Tenant ID *:", text_color="red").grid(row=1, column=0, padx=15, pady=6, sticky="e")
        self.complaint_tid_entry = ctk.CTkEntry(log_frame, width=200)
        self.complaint_tid_entry.grid(row=1, column=1, padx=15, pady=6, sticky="w")

        ctk.CTkLabel(log_frame, text="Subject *:", text_color="red").grid(row=2, column=0, padx=15, pady=6, sticky="e")
        self.complaint_subject_entry = ctk.CTkEntry(log_frame, width=300)
        self.complaint_subject_entry.grid(row=2, column=1, padx=15, pady=6, sticky="w")

        ctk.CTkLabel(log_frame, text="Description *:", text_color="red").grid(row=3, column=0, padx=15, pady=6, sticky="ne")
        self.complaint_desc_entry = ctk.CTkEntry(log_frame, width=300, placeholder_text="Describe the complaint...")
        self.complaint_desc_entry.grid(row=3, column=1, padx=15, pady=6, sticky="w")

        ctk.CTkButton(log_frame, text="Log Complaint", command=self.do_log_complaint, width=200).grid(
            row=4, column=0, columnspan=2, pady=10)

        # ─── All Complaints Table ───
        tree_frame = ctk.CTkFrame(self.tab_complaints, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Tenant", "Subject", "Date", "Status", "Description")
        self.complaints_tree = setup_treeview_scroll(tree_frame, columns=cols, height=10)

        # ─── Action Buttons ───
        btn_frame = ctk.CTkFrame(self.tab_complaints, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(btn_frame, text="Resolve Selected", command=self.do_resolve_complaint,
                       width=180, fg_color="green", hover_color="darkgreen").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_complaints, width=100).pack(side="left", padx=10)

        self.refresh_complaints()

    def do_log_complaint(self):
        tid = self.complaint_tid_entry.get()
        subject = self.complaint_subject_entry.get()
        desc = self.complaint_desc_entry.get()

        if not tid:
            messagebox.showwarning("Missing Field", "Tenant ID is required.")
            return
        try:
            self.tenant_manager.log_complaint(int(tid), subject, desc)
            messagebox.showinfo("Success", "Complaint logged!")
            self.complaint_tid_entry.delete(0, "end")
            self.complaint_subject_entry.delete(0, "end")
            self.complaint_desc_entry.delete(0, "end")
            self.refresh_complaints()
        except ValueError:
            messagebox.showerror("Error", "Tenant ID must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_resolve_complaint(self):
        selected = self.complaints_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a complaint from the table first.")
            return
        item = self.complaints_tree.item(selected[0])
        complaint_id = item["values"][0]

        if not messagebox.askyesno("Confirm", f"Resolve complaint #{complaint_id}?"):
            return
        try:
            self.tenant_manager.resolve_complaint(int(complaint_id))
            messagebox.showinfo("Success", f"Complaint #{complaint_id} resolved!")
            self.refresh_complaints()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_complaints(self):
        for item in self.complaints_tree.get_children():
            self.complaints_tree.delete(item)
        for c in self.tenant_manager.get_all_complaints():
            # (id, tenant_name, subject, date_logged, status, description)
            self.complaints_tree.insert("", "end", values=(
                c[0], c[1], c[2], c[3], c[4], c[5] or ""))
        apply_row_stripes(self.complaints_tree)
        autofit_columns(self.complaints_tree)

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_filter.set("Active")
        self.refresh_list()

    def build_actions_tab(self):
        frame = ctk.CTkFrame(self.tab_actions)
        frame.pack(pady=40)

        ctk.CTkLabel(frame, text="Tenant ID *:", font=("Arial", 14), text_color="red").grid(row=0, column=0, padx=15, pady=10, sticky="e")
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
        scroll = ctk.CTkScrollableFrame(self.tab_assign, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        frame = ctk.CTkFrame(scroll)
        frame.pack(pady=20)

        fields = [
            ("Tenant User ID *:", "t_id"),
            ("Apartment ID *:", "apt_id"),
            ("Lease Start (YYYY-MM-DD) *:", "start"),
            ("Lease End (YYYY-MM-DD) *:", "end"),
            ("Monthly Rent (£) *:", "rent"),
            ("Deposit (£) *:", "deposit"),
        ]
        self.assign_entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(frame, text=label, font=("Arial", 13), text_color="red").grid(row=i, column=0, padx=15, pady=8, sticky="e")
            entry = ctk.CTkEntry(frame, width=220)
            entry.grid(row=i, column=1, padx=15, pady=8, sticky="w")
            self.assign_entries[key] = entry

        self.assign_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.assign_result.grid(row=len(fields), column=0, columnspan=2, pady=5)

        ctk.CTkButton(frame, text="Assign Apartment", command=self.do_assign, width=280).grid(
            row=len(fields) + 1, column=0, columnspan=2, pady=12)
        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

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
            messagebox.showwarning("Missing Field", "NI Number, Full Name, Username, and Password are required (marked with *)")
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
            messagebox.showwarning("Missing Field", "Please enter a Tenant ID.")
            return

        # Validate FIRST, before asking for confirmation
        try:
            tid_int = int(tid)
        except ValueError:
            messagebox.showerror("Invalid Input", "Tenant ID must be a number.")
            return

        tenant = self.db_manager.fetch_one(
            "SELECT full_name, status, monthly_rent FROM tenants WHERE user_id=?", (tid_int,))
        if not tenant:
            messagebox.showerror("Not Found", f"No tenant found with ID {tid_int}.")
            return
        if tenant[1] in ("Terminated", "Archived"):
            messagebox.showerror("Invalid Action", f"Tenant '{tenant[0]}' is already {tenant[1]}.")
            return

        # Now show confirmation with tenant name
        penalty = tenant[2] * 0.05 if tenant[2] else 0
        if not messagebox.askyesno("Confirm Termination",
                f"Terminate lease for '{tenant[0]}'?\n\n"
                f"A 1-month notice period will apply.\n"
                f"A 5% penalty of £{penalty:.2f} will be applied."):
            return

        try:
            result = self.tenant_manager.early_termination(tid_int)
            messagebox.showinfo("Lease Terminated",
                f"Lease for '{tenant[0]}' has been terminated.\n\n"
                f"1-month notice period ends: {result['effective_date']}\n"
                f"Penalty applied: £{result['penalty']:.2f}")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_archive(self):
        tid = self.action_id_entry.get()
        if not tid:
            messagebox.showwarning("Missing Field", "Please enter a Tenant ID.")
            return

        # Validate FIRST, before asking for confirmation
        try:
            tid_int = int(tid)
        except ValueError:
            messagebox.showerror("Invalid Input", "Tenant ID must be a number.")
            return

        tenant = self.db_manager.fetch_one(
            "SELECT full_name, status FROM tenants WHERE user_id=?", (tid_int,))
        if not tenant:
            messagebox.showerror("Not Found", f"No tenant found with ID {tid_int}.")
            return
        if tenant[1] == "Archived":
            messagebox.showerror("Invalid Action", f"Tenant '{tenant[0]}' is already Archived.")
            return

        if not messagebox.askyesno("Confirm Archive",
                f"Permanently archive tenant '{tenant[0]}'?\nThis cannot be undone."):
            return

        try:
            self.tenant_manager.archive_tenant(tid_int)
            messagebox.showinfo("Tenant Archived",
                f"Tenant '{tenant[0]}' has been successfully archived.")
            self.refresh_list()
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
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)
        if hasattr(self, 'archived_tree'):
            self.refresh_archived()
