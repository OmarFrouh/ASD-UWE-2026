import tkinter as tk
from tkinter import ttk, messagebox

class UserView:
    def __init__(self, parent_frame, auth_manager):
        self.parent = parent_frame
        self.auth_manager = auth_manager
        
        # --- Layout ---
        # Title
        tk.Label(self.parent, text="User Management", font=("Arial", 18, "bold"), bg="white").pack(pady=20)
        
        # 1. Add User Form
        form_frame = tk.LabelFrame(self.parent, text="Create New User", bg="white", padx=20, pady=20)
        form_frame.pack(pady=10)
        
        # Username
        tk.Label(form_frame, text="Username:", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        tk.Label(form_frame, text="Password:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Role
        tk.Label(form_frame, text="Role:", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.role_combo = ttk.Combobox(form_frame, values=["staff", "manager", "admin", "maintenance"], state="readonly")
        self.role_combo.grid(row=2, column=1, padx=5, pady=5)
        self.role_combo.current(0)
        self.role_combo.bind("<<ComboboxSelected>>", self.toggle_staff_fields)

        # Staff Fields (Employee ID & Department) - Initially Hidden
        self.lbl_empid = tk.Label(form_frame, text="Employee ID:", bg="white")
        self.entry_empid = tk.Entry(form_frame)
        
        self.lbl_dept = tk.Label(form_frame, text="Department:", bg="white")
        self.entry_dept = tk.Entry(form_frame)
        
        # Trigger initial toggle
        self.toggle_staff_fields()
        
        # Add Button
        tk.Button(form_frame, text="Create User", command=self.create_user, bg="#4CAF50", fg="black").grid(row=5, column=0, columnspan=2, pady=15)
        
        # 2. Existing Users List (Optional for now, but good to have)
        # We need a method in AuthManager/DB to fetch_all users to populate this.
        # Implemented as a Placeholder label for now.
        tk.Label(self.parent, text="Existing Users List (Coming Soon)", bg="white", fg="gray").pack(pady=20)

    def toggle_staff_fields(self, event=None):
        role = self.role_combo.get()
        # Show fields if role is 'staff' or 'manager' or 'maintenance'
        if role in ["staff", "manager", "maintenance"]:
            self.lbl_empid.grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.entry_empid.grid(row=3, column=1, padx=5, pady=5)
            self.lbl_dept.grid(row=4, column=0, padx=5, pady=5, sticky="e")
            self.entry_dept.grid(row=4, column=1, padx=5, pady=5)
        else:
            self.lbl_empid.grid_remove()
            self.entry_empid.grid_remove()
            self.lbl_dept.grid_remove()
            self.entry_dept.grid_remove()

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_combo.get()
        
        # Get optional fields
        employee_id = self.entry_empid.get()
        department = self.entry_dept.get()
        
        if not username or not password:
            messagebox.showwarning("Validation Error", "Please fill in all fields.")
            return
            
        try:
            # Pass extra args to AuthManager
            self.auth_manager.create_user(username, password, role, employee_id, department)
            
            messagebox.showinfo("Success", f"User '{username}' created successfully!")
            
            # Clear form
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.entry_empid.delete(0, 'end')
            self.entry_dept.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not create user.\n{e}")
