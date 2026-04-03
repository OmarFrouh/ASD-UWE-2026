# 🟢 SPRINT 2 GUIDE — OMAR (Group Leader)
**Role**: Reports Module Foundation + Notification System + Sprint 2 Integration
**Do this FIRST — everyone else depends on your push!**

## Step 0: Project Management (Before Coding)

1. **Update GitHub Project Board**: Move Sprint 2 cards to "In Progress"
2. **Update `BACKLOG.md`**: Mark Reporting items as `[In Progress]`
3. **Team standup**: Message the group chat: "Sprint 2 started. Pull from dev after I push."

---

## Step 1: Update `seed_db.py`

We need overdue invoice and maintenance data so that Sprint 2 features (reports, late payment notifications) have something to render. Open `seed_db.py` and **add the following lines before `conn.commit()`** (after the tenants insert block):

```python
    # 5. Invoices (for Sprint 2 reporting & overdue testing)
    from datetime import datetime, timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    thirty_ago = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
    due_past = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    due_future = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")

    invoices = [
        # (tenant_id, issue_date, due_date, total_amount, status)
        (6, thirty_ago, due_past, 850.00, "Pending"),    # John — OVERDUE (past due date, still Pending)
        (6, today, due_future, 850.00, "Pending"),        # John — upcoming, not overdue
        (7, thirty_ago, due_past, 1100.00, "Paid"),       # Sarah — paid on time
        (7, today, due_future, 1100.00, "Pending"),       # Sarah — upcoming, not overdue
    ]
    for inv in invoices:
        cursor.execute("INSERT OR IGNORE INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)", inv)

    # 6. Payments (partial data for financial summary)
    payments = [
        # (invoice_id, amount, payment_date, method, transaction_ref)
        (3, 1100.00, thirty_ago, "Bank Transfer", "TXN-001"),  # Sarah's paid invoice
    ]
    for pay in payments:
        cursor.execute("INSERT OR IGNORE INTO payments (invoice_id, amount, payment_date, method, transaction_ref) VALUES (?,?,?,?,?)", pay)

    # 7. Maintenance requests (for cost reporting)
    maint_requests = [
        # (apartment_id, tenant_id, staff_id, description, priority, status, date_reported, time_spent, cost)
        (1, 6, 4, "Leaking kitchen tap", "High", "Fixed", thirty_ago, 2.5, 150.00),
        (3, 7, 4, "Broken window latch", "Medium", "Fixed", thirty_ago, 1.0, 75.00),
        (1, 6, None, "Flickering hallway light", "Low", "Open", today, None, None),
    ]
    for mr in maint_requests:
        cursor.execute("""INSERT OR IGNORE INTO maintenance_requests
            (apartment_id, tenant_id, staff_id, description, priority, status, date_reported, time_spent, cost)
            VALUES (?,?,?,?,?,?,?,?,?)""", mr)
```

---

## Step 2: Create `report_manager.py` (project root)

This is the backend for the Reports tab. It contains three report types matching the brief:
1. **Occupancy Report** — occupied vs vacant, filtered by city
2. **Financial Summary** — collected vs pending rent
3. **Maintenance Cost Report** — costs grouped by apartment/city

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

class ReportManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_occupancy_report(self, city=None):
        """Occupancy report filtered by apartment or city.
        Returns: list of (unit_number, address, city, rooms, rent, status)"""
        if city and city != "All":
            return self.db_manager.fetch_all("""
                SELECT unit_number, address, city, number_of_rooms, rental_price, status
                FROM apartments WHERE city = ?
                ORDER BY unit_number
            """, (city,))
        return self.db_manager.fetch_all("""
            SELECT unit_number, address, city, number_of_rooms, rental_price, status
            FROM apartments ORDER BY city, unit_number
        """)

    def get_occupancy_summary(self, city=None):
        """Returns dict with total, occupied, vacant counts."""
        if city and city != "All":
            total = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE city = ?", (city,))[0]
            occupied = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE status = 'Occupied' AND city = ?", (city,))[0]
        else:
            total = self.db_manager.fetch_one("SELECT COUNT(*) FROM apartments")[0]
            occupied = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE status = 'Occupied'")[0]
        return {
            "total": total,
            "occupied": occupied,
            "vacant": total - occupied,
            "occupancy_rate": round((occupied / total * 100), 1) if total > 0 else 0
        }

    def get_financial_summary(self):
        """Financial summary: collected vs pending rents.
        Returns dict with collected, pending, total_invoiced."""
        collected = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(amount), 0) FROM payments")[0]
        pending = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'Pending'")[0]
        total_invoiced = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices")[0]
        return {
            "collected": collected,
            "pending": pending,
            "total_invoiced": total_invoiced,
            "collection_rate": round((collected / total_invoiced * 100), 1) if total_invoiced > 0 else 0
        }

    def get_financial_breakdown(self):
        """Per-tenant financial breakdown.
        Returns: list of (tenant_name, total_invoiced, total_paid, outstanding)"""
        return self.db_manager.fetch_all("""
            SELECT t.full_name,
                   COALESCE(SUM(i.total_amount), 0) AS total_invoiced,
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             JOIN invoices i2 ON p.invoice_id = i2.id
                             WHERE i2.tenant_id = t.user_id), 0) AS total_paid,
                   COALESCE(SUM(i.total_amount), 0) -
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             JOIN invoices i2 ON p.invoice_id = i2.id
                             WHERE i2.tenant_id = t.user_id), 0) AS outstanding
            FROM tenants t
            LEFT JOIN invoices i ON t.user_id = i.tenant_id
            WHERE t.status = 'Active'
            GROUP BY t.user_id
            ORDER BY outstanding DESC
        """)

    def get_maintenance_cost_report(self, city=None):
        """Maintenance cost report grouped by apartment.
        Returns: list of (unit_number, city, total_tickets, total_cost, total_hours)"""
        if city and city != "All":
            return self.db_manager.fetch_all("""
                SELECT a.unit_number, a.city,
                       COUNT(m.id) AS total_tickets,
                       COALESCE(SUM(m.cost), 0) AS total_cost,
                       COALESCE(SUM(m.time_spent), 0) AS total_hours
                FROM maintenance_requests m
                JOIN apartments a ON m.apartment_id = a.id
                WHERE a.city = ?
                GROUP BY a.unit_number
                ORDER BY total_cost DESC
            """, (city,))
        return self.db_manager.fetch_all("""
            SELECT a.unit_number, a.city,
                   COUNT(m.id) AS total_tickets,
                   COALESCE(SUM(m.cost), 0) AS total_cost,
                   COALESCE(SUM(m.time_spent), 0) AS total_hours
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.unit_number
            ORDER BY total_cost DESC
        """)

    def get_maintenance_cost_summary(self):
        """Returns dict with total maintenance spend and average cost."""
        result = self.db_manager.fetch_one("""
            SELECT COALESCE(SUM(cost), 0), COALESCE(AVG(cost), 0),
                   COALESCE(SUM(time_spent), 0), COUNT(*)
            FROM maintenance_requests WHERE cost IS NOT NULL
        """)
        return {
            "total_cost": result[0],
            "avg_cost": round(result[1], 2),
            "total_hours": result[2],
            "completed_tickets": result[3]
        }

    def get_cities(self):
        """Returns list of all cities for filter dropdowns."""
        rows = self.db_manager.fetch_all("SELECT DISTINCT city FROM apartments ORDER BY city")
        return [row[0] for row in rows]
```

---

## Step 3: Create `notification_manager.py` (project root)

This handles automated late payment notifications as required by the brief.

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

from datetime import datetime

class NotificationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_overdue_invoices(self):
        """Returns all invoices that are past their due date and still Pending.
        Returns: list of (invoice_id, tenant_name, due_date, amount, days_overdue)"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, i.due_date, i.total_amount,
                   CAST(julianday(?) - julianday(i.due_date) AS INTEGER) AS days_overdue
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.user_id
            WHERE i.status = 'Pending' AND i.due_date < ?
            ORDER BY days_overdue DESC
        """, (today, today))

    def get_upcoming_maintenance(self):
        """Returns maintenance tickets with scheduled dates in the next 7 days.
        Returns: list of (ticket_id, unit_number, tenant_name, description, scheduled_date)"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT m.id, a.unit_number, t.full_name, m.description, m.scheduled_date
            FROM maintenance_requests m
            LEFT JOIN apartments a ON m.apartment_id = a.id
            LEFT JOIN tenants t ON m.tenant_id = t.user_id
            WHERE m.scheduled_date IS NOT NULL
              AND m.scheduled_date >= ?
              AND m.status IN ('Assigned', 'In Progress')
            ORDER BY m.scheduled_date
        """, (today,))

    def get_expiring_leases(self, days=30):
        """Returns tenants whose leases expire within the given number of days.
        Returns: list of (tenant_id, name, lease_end_date, apartment_unit, days_remaining)"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.full_name, t.lease_end_date, a.unit_number,
                   CAST(julianday(t.lease_end_date) - julianday(?) AS INTEGER) AS days_remaining
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
              AND t.lease_end_date IS NOT NULL
              AND julianday(t.lease_end_date) - julianday(?) <= ?
              AND julianday(t.lease_end_date) - julianday(?) >= 0
            ORDER BY days_remaining
        """, (today, today, days, today))

    def get_notification_count(self):
        """Returns total number of active notifications (for badge display)."""
        overdue = len(self.get_overdue_invoices())
        expiring = len(self.get_expiring_leases())
        return overdue + expiring
```

---

## Step 4: Create `views/report_view.py`

This is the Reports tab visible to Admin and Manager roles. It shows all 3 report types with city filtering.

```python
# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import ttk
from report_manager import ReportManager
from views.ui_helpers import setup_treeview_scroll

class ReportView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.report_manager = ReportManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="📈 Reports", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        # Tab view for 3 report types
        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_occupancy = self.tabview.add("Occupancy")
        tab_financial = self.tabview.add("Financial Summary")
        tab_maintenance = self.tabview.add("Maintenance Costs")

        self.build_occupancy_tab(tab_occupancy)
        self.build_financial_tab(tab_financial)
        self.build_maintenance_tab(tab_maintenance)

    # ─── OCCUPANCY REPORT ───────────────────────────────────
    def build_occupancy_tab(self, tab):
        # Filter bar
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="Filter by City:", font=("Arial", 13)).pack(side="left", padx=(10, 5))
        cities = ["All"] + self.report_manager.get_cities()
        self.occ_city_filter = ctk.CTkComboBox(filter_frame, values=cities, width=180,
                                                command=lambda _: self.refresh_occupancy())
        self.occ_city_filter.pack(side="left", padx=5)
        self.occ_city_filter.set("All")

        # Summary cards
        self.occ_summary_frame = ctk.CTkFrame(tab)
        self.occ_summary_frame.pack(fill="x", padx=10, pady=5)

        # Data table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Unit", "Address", "City", "Rooms", "Rent", "Status")
        self.occ_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)
        for c in cols:
            self.occ_tree.heading(c, text=c)
            self.occ_tree.column(c, width=100)

        self.refresh_occupancy()

    def refresh_occupancy(self):
        city = self.occ_city_filter.get()

        # Update summary cards
        for w in self.occ_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_occupancy_summary(city)
        cards = [
            ("Total", str(summary["total"])),
            ("Occupied", str(summary["occupied"])),
            ("Vacant", str(summary["vacant"])),
            ("Rate", f"{summary['occupancy_rate']}%"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.occ_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.occ_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 28, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.occ_tree.get_children():
            self.occ_tree.delete(item)
        for apt in self.report_manager.get_occupancy_report(city):
            self.occ_tree.insert("", "end", values=(
                apt[0], apt[1], apt[2], apt[3], f"£{apt[4]:.2f}", apt[5]))

    # ─── FINANCIAL SUMMARY ──────────────────────────────────
    def build_financial_tab(self, tab):
        # Summary cards
        self.fin_summary_frame = ctk.CTkFrame(tab)
        self.fin_summary_frame.pack(fill="x", padx=10, pady=10)

        # Per-tenant breakdown table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Tenant", "Total Invoiced", "Total Paid", "Outstanding")
        self.fin_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)
        for c in cols:
            self.fin_tree.heading(c, text=c)
            self.fin_tree.column(c, width=130)

        ctk.CTkButton(tab, text="🔄 Refresh", command=self.refresh_financial).pack(pady=5)
        self.refresh_financial()

    def refresh_financial(self):
        # Update summary cards
        for w in self.fin_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_financial_summary()
        cards = [
            ("Collected", f"£{summary['collected']:.2f}"),
            ("Pending", f"£{summary['pending']:.2f}"),
            ("Total Invoiced", f"£{summary['total_invoiced']:.2f}"),
            ("Collection Rate", f"{summary['collection_rate']}%"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.fin_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.fin_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 24, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.fin_tree.get_children():
            self.fin_tree.delete(item)
        for row in self.report_manager.get_financial_breakdown():
            self.fin_tree.insert("", "end", values=(
                row[0], f"£{row[1]:.2f}", f"£{row[2]:.2f}", f"£{row[3]:.2f}"))

    # ─── MAINTENANCE COST REPORT ────────────────────────────
    def build_maintenance_tab(self, tab):
        # Filter bar
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="Filter by City:", font=("Arial", 13)).pack(side="left", padx=(10, 5))
        cities = ["All"] + self.report_manager.get_cities()
        self.mnt_city_filter = ctk.CTkComboBox(filter_frame, values=cities, width=180,
                                                command=lambda _: self.refresh_maintenance())
        self.mnt_city_filter.pack(side="left", padx=5)
        self.mnt_city_filter.set("All")

        # Summary cards
        self.mnt_summary_frame = ctk.CTkFrame(tab)
        self.mnt_summary_frame.pack(fill="x", padx=10, pady=5)

        # Data table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Unit", "City", "Tickets", "Total Cost", "Total Hours")
        self.mnt_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)
        for c in cols:
            self.mnt_tree.heading(c, text=c)
            self.mnt_tree.column(c, width=110)

        self.refresh_maintenance()

    def refresh_maintenance(self):
        city = self.mnt_city_filter.get()

        # Update summary
        for w in self.mnt_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_maintenance_cost_summary()
        cards = [
            ("Total Spend", f"£{summary['total_cost']:.2f}"),
            ("Avg Cost", f"£{summary['avg_cost']:.2f}"),
            ("Total Hours", f"{summary['total_hours']:.1f}h"),
            ("Completed", str(summary["completed_tickets"])),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.mnt_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.mnt_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 24, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.mnt_tree.get_children():
            self.mnt_tree.delete(item)
        for row in self.report_manager.get_maintenance_cost_report(city):
            self.mnt_tree.insert("", "end", values=(
                row[0], row[1], row[2], f"£{row[3]:.2f}", f"{row[4]:.1f}h"))
```

---

## Step 5: Update `views/main_view.py`

In the `show_view` method, replace the reports placeholder with the real report view. Find this line:

```python
        elif view_name == "reports":
            ctk.CTkLabel(self.content_frame, text="📈 Reports — Coming Sprint 2", font=("Arial", 20)).pack(pady=50)
```

**Replace it with:**

```python
        elif view_name == "reports":
            from views.report_view import ReportView
            ReportView(self.content_frame, self.db_manager)
```

---

## Step 6: Seed & Test

```bash
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py
```

**Test these scenarios:**
| Login | What to check |
|-------|---------------|
| `admin` / `admin123` | Click Reports → Occupancy tab shows 5 apartments, filter by "Bristol" shows 2 |
| `admin` / `admin123` | Click Reports → Financial Summary shows collected vs pending with per-tenant breakdown |
| `admin` / `admin123` | Click Reports → Maintenance Costs shows cost per apartment |
| `manager1` / `pass123` | Reports tab is visible and fully functional |

---

## Step 7: Commit & Push

```bash
git checkout dev
git pull origin dev
git add report_manager.py notification_manager.py views/report_view.py views/main_view.py seed_db.py
# DO NOT add CLAUDE.md or .claude/
git commit -m "Sprint 2 (Omar): Reports module (occupancy, financial, maintenance cost), notification manager, updated seed"
git push origin dev
```

**Then message the team**: "Sprint 2 foundation pushed. Pull from dev before starting your tasks!"
