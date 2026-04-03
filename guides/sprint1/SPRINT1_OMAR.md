# 🟢 SPRINT 1 GUIDE — OMAR (Group Leader)
**Role**: Foundation Setup + CustomTkinter Migration
**Do this FIRST — everyone else depends on your push!**

## Step 0: Project Management (Before Coding)

1. **Update GitHub Project Board**: Move Sprint 1 cards to "In Progress"
2. **Update `BACKLOG.md`**: Mark your items as `[In Progress]`
3. **Team standup**: Message the group chat: "Sprint 1 started. Pull from dev after I push."

---

## Step 1: Install CustomTkinter

```bash
cd ~/Desktop/ASD-UWE-2026
source venv/bin/activate
pip install customtkinter
pip freeze > requirements.txt
```

---

## Step 2: Delete Old Database

```bash
rm -f pams.db
```

---

## Step 3: Replace `database_manager.py`

Open `database_manager.py` and **replace the entire file** with:

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import sqlite3

class DatabaseManager:
    def __init__(self, db_name="pams.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def execute_query(self, query, params=()):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

    def fetch_all(self, query, params=()):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return []

    def fetch_one(self, query, params=()):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

    def create_tables(self):
        # 1. Users
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            );
        """)

        # 2. Staff
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS staff (
                user_id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                department TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 3. Apartments (Updated: city, number_of_rooms)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT UNIQUE NOT NULL,
                address TEXT,
                city TEXT DEFAULT 'Bristol',
                number_of_rooms INTEGER DEFAULT 1,
                rental_price REAL,
                square_footage INTEGER,
                status TEXT DEFAULT 'Vacant'
            );
        """)

        # 4. Tenants (Updated: NI, occupation, references, etc.)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tenants (
                user_id INTEGER PRIMARY KEY,
                ni_number TEXT UNIQUE,
                full_name TEXT NOT NULL,
                phone_number TEXT,
                email TEXT,
                occupation TEXT,
                references_info TEXT,
                emergency_contact TEXT,
                apartment_requirements TEXT,
                apartment_id INTEGER UNIQUE,
                lease_start_date TEXT,
                lease_end_date TEXT,
                deposit_amount REAL,
                monthly_rent REAL,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE SET NULL
            );
        """)

        # 5. Maintenance Requests (Updated: tenant_id, costs, scheduling)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER NOT NULL,
                tenant_id INTEGER,
                staff_id INTEGER,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                date_reported TEXT DEFAULT CURRENT_TIMESTAMP,
                scheduled_date TEXT,
                date_resolved TEXT,
                time_spent REAL,
                cost REAL,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id),
                FOREIGN KEY (staff_id) REFERENCES staff (user_id) ON DELETE SET NULL
            );
        """)

        # 6. Invoices
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                issue_date TEXT,
                due_date TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id) ON DELETE CASCADE
            );
        """)

        # 7. Payments
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL,
                payment_date TEXT,
                method TEXT,
                transaction_ref TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            );
        """)

        print("✅ Database schema created successfully.")

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_tables()
```

---

## Step 4: Update `auth_manager.py`

Open `auth_manager.py` and **replace the entire file** with:

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import bcrypt

class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username=?"
        user_record = self.db_manager.fetch_one(query, (username,))

        if not user_record:
            return None

        stored_hash = user_record[2]
        if self.verify_hash(password, stored_hash):
            return user_record
        return None

    def verify_hash(self, plain_password, hashed_password):
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def create_user(self, username, password, role="staff", employee_id=None, department=None):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            new_user_id = cursor.lastrowid

            if role in ["staff", "manager", "maintenance", "front_desk", "finance_manager"]:
                if not employee_id:
                    raise Exception("Employee ID is required for staff roles.")
                cursor.execute(
                    "INSERT INTO staff (user_id, employee_id, department) VALUES (?, ?, ?)",
                    (new_user_id, employee_id, department)
                )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_dashboard_stats(self):
        stats = {}
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                stats["Total Users"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM staff")
                stats["Total Staff"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM apartments")
                stats["Apartments"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM apartments WHERE status='Vacant'")
                stats["Vacant"] = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"Error": 0}
        return stats
```

---

## Step 5: Update `property_manager.py`

**Replace entire file:**

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

class PropertyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_apartment(self, unit_number, address, rental_price, square_footage, city="Bristol", number_of_rooms=1):
        if not unit_number or not address:
            raise ValueError("Unit number and address are required.")
        rental_price = float(rental_price)
        square_footage = int(square_footage)
        number_of_rooms = int(number_of_rooms)

        query = """
            INSERT INTO apartments (unit_number, address, city, number_of_rooms, rental_price, square_footage)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db_manager.execute_query(query, (unit_number, address, city, number_of_rooms, rental_price, square_footage))
        return True

    def get_all_apartments(self):
        return self.db_manager.fetch_all("SELECT * FROM apartments")

    def get_vacant_apartments(self):
        return self.db_manager.fetch_all("SELECT * FROM apartments WHERE status='Vacant'")

    def update_status(self, apartment_id, status):
        self.db_manager.execute_query("UPDATE apartments SET status=? WHERE id=?", (status, apartment_id))
```

---

## Step 6: Replace `main.py`

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from database_manager import DatabaseManager
from auth_manager import AuthManager
from property_manager import PropertyManager
from views.login_view import LoginView
from views.main_view import MainView
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def main():
    try:
        db_manager = DatabaseManager("pams.db")
        db_manager.create_tables()
        auth_manager = AuthManager(db_manager)
        property_manager = PropertyManager(db_manager)

        root = ctk.CTk()

        def launch_dashboard(user):
            for widget in root.winfo_children():
                widget.destroy()
            MainView(root, auth_manager, property_manager, db_manager, user)

        LoginView(root, auth_manager, launch_dashboard)

        print("Starting PAMS...")
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Step 7: Replace `views/login_view.py`

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox

class LoginView:
    def __init__(self, root, auth_manager, on_login_success):
        self.root = root
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        self.root.title("PAMS - Login")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        frame = ctk.CTkFrame(root, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🏢 PAMS", font=("Arial", 28, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(frame, text="Paragon Apartment Management", font=("Arial", 13), text_color="gray").pack(pady=(0, 25))

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=8, padx=40)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="•", width=280, height=40)
        self.password_entry.pack(pady=8, padx=40)

        ctk.CTkButton(frame, text="Login", command=self.handle_login, width=280, height=40, font=("Arial", 14, "bold")).pack(pady=20)

        self.status_label = ctk.CTkLabel(frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=(0, 20))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Please enter both fields", text_color="orange")
            return

        user = self.auth_manager.login(username, password)
        if user:
            self.status_label.configure(text="Login Successful!", text_color="green")
            self.on_login_success(user)
        else:
            self.status_label.configure(text="Invalid Username or Password", text_color="red")
```

---

## Step 8: Replace `views/main_view.py`

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox

class MainView:
    def __init__(self, root, auth_manager, property_manager, db_manager, current_user):
        self.root = root
        self.auth_manager = auth_manager
        self.property_manager = property_manager
        self.db_manager = db_manager
        self.current_user = current_user

        self.root.title("PAMS - Dashboard")
        self.root.geometry("1200x700")

        # Header
        header = ctk.CTkFrame(root, height=50, corner_radius=0)
        header.pack(side="top", fill="x")
        ctk.CTkLabel(header, text="🏢 Paragon Apartment Management System", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text=f"👤 {self.current_user[1]} ({self.current_user[3]})", font=("Arial", 12)).pack(side="right", padx=20)

        # Sidebar
        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.setup_sidebar()

        # Content
        self.content_frame = ctk.CTkFrame(root, corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")
        self.show_view("dashboard")

    def setup_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="Navigation", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        role = self.current_user[3]

        ctk.CTkButton(self.sidebar, text="📊 Dashboard", command=lambda: self.show_view("dashboard"), width=180).pack(pady=4, padx=10)

        if role == "admin":
            ctk.CTkButton(self.sidebar, text="👥 Users", command=lambda: self.show_view("users"), width=180).pack(pady=4, padx=10)

        ctk.CTkButton(self.sidebar, text="🏠 Apartments", command=lambda: self.show_view("apartments"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "front_desk", "manager"]:
            ctk.CTkButton(self.sidebar, text="👤 Tenants", command=lambda: self.show_view("tenants"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "finance_manager"]:
            ctk.CTkButton(self.sidebar, text="💰 Invoices", command=lambda: self.show_view("invoices"), width=180).pack(pady=4, padx=10)
            ctk.CTkButton(self.sidebar, text="💳 Payments", command=lambda: self.show_view("payments"), width=180).pack(pady=4, padx=10)

        ctk.CTkButton(self.sidebar, text="🔧 Maintenance", command=lambda: self.show_view("maintenance"), width=180).pack(pady=4, padx=10)

        if role in ["admin", "manager"]:
            ctk.CTkButton(self.sidebar, text="📈 Reports", command=lambda: self.show_view("reports"), width=180).pack(pady=4, padx=10)

        ctk.CTkButton(self.sidebar, text="🚪 Logout", command=self.logout, width=180, fg_color="red", hover_color="darkred").pack(side="bottom", pady=20, padx=10)

    def check_permissions(self, permission):
        role = self.current_user[3]
        if permission == "manage_users":
            return role == 'admin'
        return False

    def show_view(self, view_name):
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
            TenantView(self.content_frame, self.db_manager)
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
            ctk.CTkLabel(self.content_frame, text="📈 Reports — Coming Sprint 2", font=("Arial", 20)).pack(pady=50)

    def show_dashboard(self):
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
            self.root.destroy()
```

---

## Step 9: Replace `views/user_view.py`

```python
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
```

---

## Step 10: Replace `views/apartment_view.py`

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk

class ApartmentView:
    def __init__(self, parent, property_manager):
        self.property_manager = property_manager

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="🏠 Apartment Management", font=("Arial", 22, "bold")).pack(pady=(0, 15))

        form = ctk.CTkFrame(frame)
        form.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(form, text="Unit #:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        self.unit_entry = ctk.CTkEntry(form, width=180)
        self.unit_entry.grid(row=0, column=1, padx=8, pady=6)

        ctk.CTkLabel(form, text="Address:").grid(row=0, column=2, padx=8, pady=6, sticky="e")
        self.address_entry = ctk.CTkEntry(form, width=180)
        self.address_entry.grid(row=0, column=3, padx=8, pady=6)

        ctk.CTkLabel(form, text="City:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        self.city_combo = ctk.CTkComboBox(form, values=["Bristol", "Cardiff", "London", "Manchester"], width=180)
        self.city_combo.grid(row=1, column=1, padx=8, pady=6)
        self.city_combo.set("Bristol")

        ctk.CTkLabel(form, text="Rooms:").grid(row=1, column=2, padx=8, pady=6, sticky="e")
        self.rooms_entry = ctk.CTkEntry(form, width=180)
        self.rooms_entry.grid(row=1, column=3, padx=8, pady=6)

        ctk.CTkLabel(form, text="Rent (£):").grid(row=2, column=0, padx=8, pady=6, sticky="e")
        self.rent_entry = ctk.CTkEntry(form, width=180)
        self.rent_entry.grid(row=2, column=1, padx=8, pady=6)

        ctk.CTkLabel(form, text="Size (sqft):").grid(row=2, column=2, padx=8, pady=6, sticky="e")
        self.size_entry = ctk.CTkEntry(form, width=180)
        self.size_entry.grid(row=2, column=3, padx=8, pady=6)

        ctk.CTkButton(form, text="Add Unit", command=self.submit_apartment, width=200).grid(row=3, column=0, columnspan=4, pady=12)

        # Table
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill="both", expand=True, pady=10, padx=20)

        cols = ("unit", "address", "city", "rooms", "rent", "sqft", "status")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for c, h in zip(cols, ["Unit", "Address", "City", "Rooms", "Rent", "Sqft", "Status"]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_list()

    def submit_apartment(self):
        try:
            self.property_manager.add_apartment(
                self.unit_entry.get(), self.address_entry.get(),
                self.rent_entry.get(), self.size_entry.get(),
                self.city_combo.get(), self.rooms_entry.get() or "1"
            )
            messagebox.showinfo("Success", "Apartment added!")
            self.clear_form()
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        for e in [self.unit_entry, self.address_entry, self.rooms_entry, self.rent_entry, self.size_entry]:
            e.delete(0, 'end')

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for apt in self.property_manager.get_all_apartments():
            # Schema: id, unit, address, city, rooms, price, sqft, status
            self.tree.insert("", "end", values=(apt[1], apt[2], apt[3], apt[4], f"£{apt[5]:.2f}", apt[6], apt[7]))
```

---

## Step 11: Replace `seed_db.py`

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import bcrypt, os
from database_manager import DatabaseManager

def seed():
    db = DatabaseManager("pams.db")
    db.create_tables()
    conn = db.get_connection()
    cursor = conn.cursor()

    def hp(pw):
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

    # Users
    users = [
        ("admin", hp("admin123"), "admin"),
        ("frontdesk1", hp("pass123"), "front_desk"),
        ("finance1", hp("pass123"), "finance_manager"),
        ("maint1", hp("pass123"), "maintenance"),
        ("manager1", hp("pass123"), "manager"),
        ("tenant1", hp("pass123"), "tenant"),
        ("tenant2", hp("pass123"), "tenant"),
    ]
    for u in users:
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", u)

    # Staff
    for s in [(2,"EMP001","Front Desk"),(3,"EMP002","Finance"),(4,"EMP003","Maintenance"),(5,"EMP004","Management")]:
        cursor.execute("INSERT OR IGNORE INTO staff (user_id, employee_id, department) VALUES (?, ?, ?)", s)

    # Apartments
    apts = [
        ("101","10 Park St","Bristol",2,850.00,650,"Occupied"),
        ("102","10 Park St","Bristol",1,600.00,450,"Vacant"),
        ("201","25 Queen Rd","Cardiff",3,1100.00,900,"Occupied"),
        ("301","5 King Ln","London",2,1500.00,700,"Vacant"),
        ("401","8 High St","Manchester",1,550.00,400,"Vacant"),
    ]
    for a in apts:
        cursor.execute("INSERT OR IGNORE INTO apartments (unit_number,address,city,number_of_rooms,rental_price,square_footage,status) VALUES (?,?,?,?,?,?,?)", a)

    # Tenants
    ts = [
        (6,"NI123456A","John Smith","07712345678","john@email.com","Engineer","Dr. Adams","Jane Smith","2 bed flat",1,"2025-01-01","2026-01-01",850.00,850.00,"Active"),
        (7,"NI789012B","Sarah Jones","07798765432","sarah@email.com","Teacher","Mr. Brown","Tom Jones","3 bed house",3,"2025-06-01","2026-06-01",1100.00,1100.00,"Active"),
    ]
    for t in ts:
        cursor.execute("INSERT OR IGNORE INTO tenants (user_id,ni_number,full_name,phone_number,email,occupation,references_info,emergency_contact,apartment_requirements,apartment_id,lease_start_date,lease_end_date,deposit_amount,monthly_rent,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)

    conn.commit()
    conn.close()
    print("✅ Database seeded!")

if __name__ == "__main__":
    if os.path.exists("pams.db"):
        os.remove("pams.db")
    seed()
```

---

## Step 12: Seed & Test

```bash
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py
```

**Test these logins:**
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin (sees everything) |
| frontdesk1 | pass123 | Front Desk (sees Tenants) |
| finance1 | pass123 | Finance Manager (sees Invoices/Payments) |
| maint1 | pass123 | Maintenance (sees Maintenance) |
| manager1 | pass123 | Manager (sees Reports) |

---

## Step 13: Commit & Push

```bash
git add -A
git commit -m "Sprint 1 (Omar): CustomTkinter migration, updated schema, role-based sidebar, mock data"
git push origin main
```

**Then message the team**: "Pull latest from main before starting your tasks!"
