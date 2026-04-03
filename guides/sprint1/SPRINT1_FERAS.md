# 🟡 SPRINT 1 GUIDE — FERAS BADER (Frontend Lead)
**Role**: Tenant Management + Use Case Diagram
**Prerequisite**: Omar must push his changes first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Register Tenant, Tenant List, Manage Leases, Early Termination, Use Case Diagram)
2. **Move cards on Project Board**: Drag your Sprint 1 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue with what you did

---

## Step 1: Setup (Read `guides/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/tenant-management
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/tenant-management && git merge dev`

---

## Step 2: Create `tenant_manager.py` (project root)

```python
# Student Name: Feras Bader
# Student ID: [YOUR_ID]

import bcrypt
from datetime import datetime

class TenantManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def register_tenant(self, username, password, ni_number, full_name, phone, email, occupation, references, emergency_contact, apt_requirements):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed, "tenant")
            )
            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email,
                    occupation, references_info, emergency_contact, apartment_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, ni_number, full_name, phone, email, occupation, references, emergency_contact, apt_requirements))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all_tenants(self):
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
            ORDER BY t.full_name
        """)

    def get_archived_tenants(self):
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.status
            FROM tenants t WHERE t.status IN ('Archived', 'Terminated')
        """)

    def assign_apartment(self, tenant_user_id, apartment_id, lease_start, lease_end, monthly_rent, deposit):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE tenants SET apartment_id=?, lease_start_date=?, lease_end_date=?,
                    monthly_rent=?, deposit_amount=? WHERE user_id=?
            """, (apartment_id, lease_start, lease_end, monthly_rent, deposit, tenant_user_id))
            cursor.execute("UPDATE apartments SET status='Occupied' WHERE id=?", (apartment_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def early_termination(self, tenant_user_id):
        tenant = self.db_manager.fetch_one("SELECT monthly_rent, apartment_id FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")

        penalty = (tenant[0] or 0) * 0.05
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tenants SET status='Terminated', lease_end_date=? WHERE user_id=?",
                           (datetime.now().strftime("%Y-%m-%d"), tenant_user_id))
            if tenant[1]:
                cursor.execute("UPDATE apartments SET status='Vacant' WHERE id=?", (tenant[1],))
            conn.commit()
            return penalty
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def archive_tenant(self, tenant_user_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            tenant = self.db_manager.fetch_one("SELECT apartment_id FROM tenants WHERE user_id=?", (tenant_user_id,))
            cursor.execute("UPDATE tenants SET status='Archived' WHERE user_id=?", (tenant_user_id,))
            if tenant and tenant[0]:
                cursor.execute("UPDATE apartments SET status='Vacant' WHERE id=?", (tenant[0],))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
```

---

## Step 3: Create `views/tenant_view.py`

```python
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
```

---

## Step 4: Use Case Diagram (Astah)

### Open `pmas.asta` in Astah. Create a **new Use Case Diagram**.

**Actors to add** (stick figures on the left and right):
- Administrator
- Front-desk Staff
- Finance Manager
- Maintenance Staff
- Manager

**Use Cases** (ovals in the center):

| # | Use Case Name | Connected Actors |
|---|---------------|------------------|
| 1 | Login | All |
| 2 | Create Staff Accounts | Administrator |
| 3 | Register Tenant | Front-desk Staff |
| 4 | View Tenant List | Front-desk Staff, Administrator |
| 5 | Manage Leases | Front-desk Staff |
| 6 | Early Lease Termination | Front-desk Staff |
| 7 | Archive Tenant | Manager |
| 8 | Add Apartment | Administrator |
| 9 | Assign Tenant to Apartment | Front-desk Staff |
| 10 | Generate Invoice | Finance Manager |
| 11 | Record Payment | Finance Manager |
| 12 | Track Late Payments | Finance Manager |
| 13 | Log Maintenance Issue | Front-desk Staff |
| 14 | Assign Maintenance Staff | Manager |
| 15 | Update Maintenance Status | Maintenance Staff |
| 16 | Log Maintenance Costs | Maintenance Staff |
| 17 | View Occupancy Report | Manager |
| 18 | View Financial Report | Finance Manager, Manager |
| 19 | View Maintenance Cost Report | Manager |
| 20 | Manage User Accounts | Administrator |

**How to draw in Astah:**
1. Right-click diagram area → New → Use Case Diagram
2. Drag "Actor" from palette for each role
3. Drag "Use Case" (oval) for each item above
4. Draw Association lines from Actor to Use Case
5. Add a System Boundary box around all use cases, label it "PAMS"

---

## Step 5: Commit & Push

```bash
git add -A
git commit -m "Sprint 1 (Feras): Tenant registration, list, early termination, archive"
git push origin feature/tenant-management
```

Then:
1. Go to **GitHub** → you'll see a yellow banner "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/tenant-management`
3. Title: `Sprint 1 (Feras): Tenant registration and management`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review
