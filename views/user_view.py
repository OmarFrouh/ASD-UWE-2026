# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes

class UserView:
    def __init__(self, parent_frame, auth_manager):
        self.parent = parent_frame
        self.auth_manager = auth_manager

        ctk.CTkLabel(self.parent, text="👥 User Management", font=("Arial", 22, "bold")).pack(pady=20)

        form = ctk.CTkFrame(self.parent)
        form.pack(pady=30)

        ctk.CTkLabel(form, text="Create New User", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ctk.CTkLabel(form, text="Username *:", text_color="red").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.username_entry = ctk.CTkEntry(form, width=250)
        self.username_entry.grid(row=1, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Password *:", text_color="red").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.password_entry = ctk.CTkEntry(form, show="•", width=250)
        self.password_entry.grid(row=2, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Role *:", text_color="red").grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.role_combo = ctk.CTkComboBox(form, values=["front_desk", "finance_manager", "maintenance", "manager", "admin"], width=250, command=self.toggle_staff_fields)
        self.role_combo.grid(row=3, column=1, padx=15, pady=8, sticky="w")
        self.role_combo.set("front_desk")

        self.lbl_empid = ctk.CTkLabel(form, text="Employee ID *:", text_color="red")
        self.entry_empid = ctk.CTkEntry(form, width=250)
        self.lbl_dept = ctk.CTkLabel(form, text="Department:")
        self.entry_dept = ctk.CTkEntry(form, width=250)

        self.toggle_staff_fields()

        ctk.CTkButton(form, text="Create User", command=self.create_user, width=250).grid(row=6, column=0, columnspan=2, pady=20)

        # ─── User List ───
        list_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        header = ctk.CTkFrame(list_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(header, text="All Users", font=("Arial", 15, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Refresh", command=self.refresh_list, width=90).pack(side="right")

        cols = ("ID", "Username", "Role", "Employee ID", "Department", "Created", "Last Login")
        self.tree = setup_treeview_scroll(list_frame, columns=cols, col_widths=[40, 120, 130, 110, 120, 140, 140], height=10)
        self.refresh_list()

    def toggle_staff_fields(self, *args):
        role = self.role_combo.get()
        if role in ["manager", "maintenance", "front_desk", "finance_manager"]:
            self.lbl_empid.grid(row=4, column=0, padx=15, pady=8, sticky="e")
            self.entry_empid.grid(row=4, column=1, padx=15, pady=8, sticky="w")
            self.lbl_dept.grid(row=5, column=0, padx=15, pady=8, sticky="e")
            self.entry_dept.grid(row=5, column=1, padx=15, pady=8, sticky="w")
        else:
            self.lbl_empid.grid_remove()
            self.entry_empid.grid_remove()
            self.lbl_dept.grid_remove()
            self.entry_dept.grid_remove()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.auth_manager.get_all_users():
            self.tree.insert("", "end", values=row)
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_combo.get()
        employee_id = self.entry_empid.get()
        department = self.entry_dept.get()

        if not username or not password:
            messagebox.showwarning("Error", "Username and password required.")
            return
        try:
            self.auth_manager.create_user(username, password, role, employee_id, department)
            messagebox.showinfo("Success", f"User '{username}' created!")
            for e in [self.username_entry, self.password_entry, self.entry_empid, self.entry_dept]:
                e.delete(0, 'end')
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
