# 🟠 SPRINT 1 GUIDE — NUMAIR (QA & Maintenance Lead)
**Role**: Maintenance Module
**Prerequisite**: Omar must push his changes first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Log Maintenance Issue, Assign Staff, Update Status, Log Costs)
2. **Move cards on Project Board**: Drag your Sprint 1 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue

---

## Step 1: Setup (Read `guides/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/maintenance-module
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/maintenance-module && git merge dev`

---

## Step 2: Create `maintenance_manager.py` (project root)

```python
# Student Name: Numair
# Student ID: [YOUR_ID]

from datetime import datetime

class MaintenanceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_ticket(self, apartment_id, tenant_id, description, priority="Medium"):
        if not description:
            raise Exception("Description is required")
        if priority not in ["Low", "Medium", "High", "Urgent"]:
            raise Exception("Priority must be Low, Medium, High, or Urgent")

        self.db_manager.execute_query("""
            INSERT INTO maintenance_requests
                (apartment_id, tenant_id, description, priority, status, date_reported)
            VALUES (?, ?, ?, ?, 'Open', ?)
        """, (apartment_id, tenant_id or None, description, priority,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True

    def get_all_tickets(self):
        return self.db_manager.fetch_all("""
            SELECT m.id, a.unit_number, t.full_name, m.description, m.priority,
                   m.status, m.date_reported, m.scheduled_date,
                   s_user.username AS assigned_to, m.time_spent, m.cost
            FROM maintenance_requests m
            LEFT JOIN apartments a ON m.apartment_id = a.id
            LEFT JOIN tenants t ON m.tenant_id = t.user_id
            LEFT JOIN staff st ON m.staff_id = st.user_id
            LEFT JOIN users s_user ON st.user_id = s_user.id
            ORDER BY
                CASE m.priority
                    WHEN 'Urgent' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                END, m.date_reported DESC
        """)

    def assign_staff(self, ticket_id, staff_user_id, scheduled_date=None):
        staff = self.db_manager.fetch_one(
            "SELECT user_id FROM staff WHERE user_id=?", (staff_user_id,))
        if not staff:
            raise Exception("Staff member not found")

        self.db_manager.execute_query("""
            UPDATE maintenance_requests
            SET staff_id=?, scheduled_date=?, status='Assigned'
            WHERE id=?
        """, (staff_user_id, scheduled_date, ticket_id))
        return True

    def update_status(self, ticket_id, new_status):
        valid = ["Open", "Assigned", "In Progress", "Fixed", "Closed"]
        if new_status not in valid:
            raise Exception(f"Status must be one of: {', '.join(valid)}")

        updates = "status=?"
        params = [new_status]

        if new_status == "Fixed":
            updates += ", date_resolved=?"
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        params.append(ticket_id)
        self.db_manager.execute_query(
            f"UPDATE maintenance_requests SET {updates} WHERE id=?", tuple(params))
        return True

    def log_costs(self, ticket_id, time_spent, cost):
        time_spent = float(time_spent)
        cost = float(cost)
        if time_spent < 0 or cost < 0:
            raise Exception("Time and cost must be positive")

        self.db_manager.execute_query("""
            UPDATE maintenance_requests SET time_spent=?, cost=? WHERE id=?
        """, (time_spent, cost, ticket_id))
        return True

    def get_available_staff(self):
        return self.db_manager.fetch_all("""
            SELECT s.user_id, u.username, s.department
            FROM staff s JOIN users u ON s.user_id = u.id
            WHERE u.role = 'maintenance'
        """)

    def get_maintenance_costs_summary(self):
        return self.db_manager.fetch_all("""
            SELECT a.unit_number, COUNT(*) as total_tickets,
                   COALESCE(SUM(m.cost), 0) as total_cost,
                   COALESCE(SUM(m.time_spent), 0) as total_hours
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.unit_number
        """)
```

---

## Step 3: Create `views/maintenance_view.py`

```python
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
        cols = ("ID", "Unit", "Tenant", "Issue", "Priority", "Status", "Reported", "Assigned To")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(tab, text="Refresh", command=self.refresh_list).pack(pady=5)
        self.refresh_list()

    def build_manage_tab(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(pady=20, padx=40)

        ctk.CTkLabel(frame, text="Ticket ID:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.manage_id = ctk.CTkEntry(frame, width=200)
        self.manage_id.grid(row=0, column=1, padx=10, pady=8)

        # Assign Staff
        ctk.CTkLabel(frame, text="── Assign Staff ──", font=("Arial", 13, "bold")).grid(row=1, column=0, columnspan=2, pady=(15,5))

        ctk.CTkLabel(frame, text="Staff User ID:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.staff_id_entry = ctk.CTkEntry(frame, width=200)
        self.staff_id_entry.grid(row=2, column=1, padx=10, pady=8)

        ctk.CTkLabel(frame, text="Scheduled Date:").grid(row=3, column=0, padx=10, pady=8, sticky="e")
        self.sched_entry = ctk.CTkEntry(frame, width=200, placeholder_text="YYYY-MM-DD")
        self.sched_entry.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkButton(frame, text="Assign", command=self.assign, width=200).grid(row=4, column=0, columnspan=2, pady=8)

        # Update Status
        ctk.CTkLabel(frame, text="── Update Status ──", font=("Arial", 13, "bold")).grid(row=5, column=0, columnspan=2, pady=(15,5))

        self.status_combo = ctk.CTkComboBox(frame, values=["Open", "Assigned", "In Progress", "Fixed", "Closed"], width=200)
        self.status_combo.grid(row=6, column=0, columnspan=2, pady=8)
        self.status_combo.set("In Progress")

        ctk.CTkButton(frame, text="Update Status", command=self.update_status, width=200).grid(row=7, column=0, columnspan=2, pady=8)

        # Log Costs
        ctk.CTkLabel(frame, text="── Log Costs ──", font=("Arial", 13, "bold")).grid(row=8, column=0, columnspan=2, pady=(15,5))

        ctk.CTkLabel(frame, text="Hours Spent:").grid(row=9, column=0, padx=10, pady=8, sticky="e")
        self.hours_entry = ctk.CTkEntry(frame, width=200)
        self.hours_entry.grid(row=9, column=1, padx=10, pady=8)

        ctk.CTkLabel(frame, text="Cost (£):").grid(row=10, column=0, padx=10, pady=8, sticky="e")
        self.cost_entry = ctk.CTkEntry(frame, width=200)
        self.cost_entry.grid(row=10, column=1, padx=10, pady=8)

        ctk.CTkButton(frame, text="Log Costs", command=self.log_costs, width=200).grid(row=11, column=0, columnspan=2, pady=15)

        self.manage_result = ctk.CTkLabel(frame, text="", font=("Arial", 12))
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
            self.desc_entry.delete(0, 'end')
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
                t[3][:30], t[4], t[5], t[6], t[8] or "Unassigned"))
```

---

## Step 4: Commit & Push

```bash
git add -A
git commit -m "Sprint 1 (Numair): Maintenance tickets, staff assignment, cost logging, status updates"
git push origin feature/maintenance-module
```

Then:
1. Go to **GitHub** → click "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/maintenance-module`
3. Title: `Sprint 1 (Numair): Maintenance module`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review

---

## Quick Reference: Available Staff for Testing

After Omar seeds the database, use these IDs for staff assignment:

| Staff User ID | Username | Department |
|---------------|----------|------------|
| 4 | maint1 | Maintenance |

Test apartment IDs: 1-5 (from seed data).
