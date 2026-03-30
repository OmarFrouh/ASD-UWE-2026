# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox

class UserView:
    def __init__(self, parent_frame, auth_manager):
        self.parent = parent_frame
        self.auth_manager = auth_manager

        ctk.CTkLabel(self.parent, text="👥 User Management", font=("Arial", 22, "bold")).pack(pady=20)

        form = ctk.CTkFrame(self.parent)
        form.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(form, text="Create New User", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ctk.CTkLabel(form, text="Username:").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.username_entry = ctk.CTkEntry(form, width=250)
        self.username_entry.grid(row=1, column=1, padx=15, pady=8)

        ctk.CTkLabel(form, text="Password:").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.password_entry = ctk.CTkEntry(form, show="•", width=250)
        self.password_entry.grid(row=2, column=1, padx=15, pady=8)

        ctk.CTkLabel(form, text="Role:").grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.role_combo = ctk.CTkComboBox(form, values=["staff", "manager", "admin", "maintenance", "finance_manager", "front_desk"], width=250, command=self.toggle_staff_fields)
        self.role_combo.grid(row=3, column=1, padx=15, pady=8)
        self.role_combo.set("staff")

        self.lbl_empid = ctk.CTkLabel(form, text="Employee ID:")
        self.entry_empid = ctk.CTkEntry(form, width=250)
        self.lbl_dept = ctk.CTkLabel(form, text="Department:")
        self.entry_dept = ctk.CTkEntry(form, width=250)

        self.toggle_staff_fields()

        ctk.CTkButton(form, text="Create User", command=self.create_user, width=250).grid(row=6, column=0, columnspan=2, pady=20)

    def toggle_staff_fields(self, *args):
        role = self.role_combo.get()
        if role in ["staff", "manager", "maintenance", "front_desk", "finance_manager"]:
            self.lbl_empid.grid(row=4, column=0, padx=15, pady=8, sticky="e")
            self.entry_empid.grid(row=4, column=1, padx=15, pady=8)
            self.lbl_dept.grid(row=5, column=0, padx=15, pady=8, sticky="e")
            self.entry_dept.grid(row=5, column=1, padx=15, pady=8)
        else:
            self.lbl_empid.grid_remove()
            self.entry_empid.grid_remove()
            self.lbl_dept.grid_remove()
            self.entry_dept.grid_remove()

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
        except Exception as e:
            messagebox.showerror("Error", str(e))
