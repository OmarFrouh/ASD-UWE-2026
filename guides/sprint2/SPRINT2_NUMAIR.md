# 🟠 SPRINT 2 GUIDE — NUMAIR (QA & Maintenance Lead)
**Role**: Maintenance Cost Report + Date Communication to Tenants
**Prerequisite**: Omar must push Sprint 2 foundation first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Maintenance Cost Report by Apartment, Cost Report by City, Communicate Dates to Tenants)
2. **Move cards on Project Board**: Drag your Sprint 2 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue

---

## Step 1: Setup (Read `guides/sprint2/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/maintenance-sprint2
source venv/bin/activate
pip install -r requirements.txt
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py    # confirm the Sprint 2 foundation loads
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/maintenance-sprint2 && git merge dev`

---

## Step 2: Update `maintenance_manager.py`

Open `maintenance_manager.py` and **add these new methods** at the bottom of the `MaintenanceManager` class:

```python
    def get_cost_report_by_apartment(self):
        """Returns maintenance cost breakdown per apartment unit.
        Used in the Reports module for budget management.
        Returns: list of (unit_number, city, total_tickets, open_tickets, resolved_tickets, total_cost, total_hours, avg_cost_per_ticket)"""
        return self.db_manager.fetch_all("""
            SELECT a.unit_number, a.city,
                   COUNT(m.id) AS total_tickets,
                   SUM(CASE WHEN m.status IN ('Open', 'Assigned', 'In Progress') THEN 1 ELSE 0 END) AS open_tickets,
                   SUM(CASE WHEN m.status IN ('Fixed', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
                   COALESCE(SUM(m.cost), 0) AS total_cost,
                   COALESCE(SUM(m.time_spent), 0) AS total_hours,
                   ROUND(COALESCE(AVG(m.cost), 0), 2) AS avg_cost
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.id
            ORDER BY total_cost DESC
        """)

    def get_cost_report_by_city(self):
        """Returns maintenance cost breakdown per city.
        Returns: list of (city, total_tickets, total_cost, total_hours, avg_cost_per_ticket)"""
        return self.db_manager.fetch_all("""
            SELECT a.city,
                   COUNT(m.id) AS total_tickets,
                   COALESCE(SUM(m.cost), 0) AS total_cost,
                   COALESCE(SUM(m.time_spent), 0) AS total_hours,
                   ROUND(COALESCE(AVG(m.cost), 0), 2) AS avg_cost
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.city
            ORDER BY total_cost DESC
        """)

    def get_tickets_by_status_count(self):
        """Returns count of tickets grouped by status.
        Returns: dict of status -> count"""
        rows = self.db_manager.fetch_all("""
            SELECT status, COUNT(*) FROM maintenance_requests GROUP BY status
        """)
        return {row[0]: row[1] for row in rows}

    def notify_tenant_scheduled_date(self, ticket_id, scheduled_date):
        """Sets the scheduled maintenance date on a ticket.
        This is the 'communicate dates' requirement from the brief.
        Returns: dict with tenant name and scheduled date for confirmation."""
        # Validate ticket exists
        ticket = self.db_manager.fetch_one(
            "SELECT id, tenant_id FROM maintenance_requests WHERE id=?", (ticket_id,))
        if not ticket:
            raise Exception("Ticket not found")

        # Update the scheduled date
        self.db_manager.execute_query(
            "UPDATE maintenance_requests SET scheduled_date=? WHERE id=?",
            (scheduled_date, ticket_id))

        # Get tenant info for confirmation
        if ticket[1]:
            tenant = self.db_manager.fetch_one(
                "SELECT full_name, phone_number, email FROM tenants WHERE user_id=?",
                (ticket[1],))
            if tenant:
                return {
                    "tenant_name": tenant[0],
                    "phone": tenant[1] or "N/A",
                    "email": tenant[2] or "N/A",
                    "scheduled_date": scheduled_date,
                    "ticket_id": ticket_id
                }
        return {
            "tenant_name": "No tenant linked",
            "scheduled_date": scheduled_date,
            "ticket_id": ticket_id
        }
```

---

## Step 3: Update `views/maintenance_view.py`

You need to add two new features:
1. A **"Cost Report"** tab showing maintenance costs per apartment and per city
2. A **"Notify Tenant"** button in the Manage tab for communicating scheduled dates

### 3a. Add the Cost Report Tab

In `__init__`, after the existing tabs, **add**:

```python
        tab_costs = self.tabview.add("Cost Report")
        self.build_cost_tab(tab_costs)
```

Then add this new method to the class:

```python
    def build_cost_tab(self, tab):
        """Builds the maintenance cost report tab with per-apartment and per-city breakdown."""
        # ─── Summary Cards ───
        self.cost_summary_frame = ctk.CTkFrame(tab)
        self.cost_summary_frame.pack(fill="x", padx=10, pady=10)

        # ─── Per-Apartment Breakdown ───
        ctk.CTkLabel(tab, text="Cost by Apartment", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        apt_frame = ctk.CTkFrame(tab, fg_color="transparent")
        apt_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Unit", "City", "Total Tickets", "Open", "Resolved", "Total Cost", "Total Hours", "Avg Cost")
        self.cost_apt_tree = setup_treeview_scroll(apt_frame, columns=cols, height=6)
        for c in cols:
            self.cost_apt_tree.column(c, width=90)

        # ─── Per-City Breakdown ───
        ctk.CTkLabel(tab, text="Cost by City", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        city_frame = ctk.CTkFrame(tab, fg_color="transparent")
        city_frame.pack(fill="both", expand=True, padx=10, pady=5)

        city_cols = ("City", "Total Tickets", "Total Cost", "Total Hours", "Avg Cost")
        self.cost_city_tree = setup_treeview_scroll(city_frame, columns=city_cols, height=5)
        for c in city_cols:
            self.cost_city_tree.column(c, width=120)

        ctk.CTkButton(tab, text="🔄 Refresh Report", command=self.refresh_cost_report).pack(pady=8)
        self.refresh_cost_report()

    def refresh_cost_report(self):
        """Refreshes the cost report data in both tables and summary cards."""
        # ─── Summary Cards ───
        for w in self.cost_summary_frame.winfo_children():
            w.destroy()
        status_counts = self.manager.get_tickets_by_status_count()
        total = sum(status_counts.values())
        cards = [("Total Tickets", str(total))]
        for status, count in status_counts.items():
            cards.append((status, str(count)))
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.cost_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            self.cost_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold")).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=label, font=("Arial", 11), text_color="gray").pack(pady=(0, 10))

        # ─── Per-Apartment Table ───
        for item in self.cost_apt_tree.get_children():
            self.cost_apt_tree.delete(item)
        for row in self.manager.get_cost_report_by_apartment():
            # unit, city, total, open, resolved, cost, hours, avg
            self.cost_apt_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4],
                f"£{row[5]:.2f}", f"{row[6]:.1f}h", f"£{row[7]:.2f}"))

        # ─── Per-City Table ───
        for item in self.cost_city_tree.get_children():
            self.cost_city_tree.delete(item)
        for row in self.manager.get_cost_report_by_city():
            # city, total, cost, hours, avg
            self.cost_city_tree.insert("", "end", values=(
                row[0], row[1], f"£{row[2]:.2f}", f"{row[3]:.1f}h", f"£{row[4]:.2f}"))
```

### 3b. Add "Notify Tenant" Section to Manage Tab

The manage tab uses `pack()` layout (not `grid()`). Add a new `pack`-based section **between** the existing `cols_frame` and `manage_result` lines.

Find this block at the end of `build_manage_tab`:

```python
        self.manage_result = ctk.CTkLabel(tab, text="", font=("Arial", 12))
        self.manage_result.pack(pady=20)
```

**Add the notify section BEFORE it** (leave `manage_result` exactly as is — do NOT change its row or parent):

```python
        # ─── Communicate Date to Tenant ───
        notify_frame = ctk.CTkFrame(tab, fg_color="transparent")
        notify_frame.pack(pady=(10, 5))

        ctk.CTkLabel(notify_frame, text="── Notify Tenant ──", font=("Arial", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(5, 10))

        ctk.CTkLabel(notify_frame, text="Maintenance Date:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.notify_date_entry = ctk.CTkEntry(notify_frame, width=200, placeholder_text="YYYY-MM-DD")
        self.notify_date_entry.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkButton(notify_frame, text="📧 Set Date & Notify Tenant",
                       command=self.notify_tenant, width=220).grid(
            row=2, column=0, columnspan=2, pady=8)

        self.manage_result = ctk.CTkLabel(tab, text="", font=("Arial", 12))
        self.manage_result.pack(pady=20)
```

> ⚠️ The `manage_result` line above is the **replacement** for the original — copy the entire block above, replacing the old two-line `manage_result` block. Do not keep both.

Finally, add the `notify_tenant` handler method:

```python
    def notify_tenant(self):
        """Handles the 'Communicate Dates' requirement from the brief."""
        tid = self.manage_id.get()
        date = self.notify_date_entry.get()
        if not tid or not date:
            messagebox.showwarning("Error", "Ticket ID and date required.")
            return
        try:
            result = self.manager.notify_tenant_scheduled_date(int(tid), date)
            msg = (f"✅ Maintenance scheduled for {result['scheduled_date']}!\n\n"
                   f"Tenant: {result['tenant_name']}\n"
                   f"Phone: {result.get('phone', 'N/A')}\n"
                   f"Email: {result.get('email', 'N/A')}\n\n"
                   f"Please contact the tenant to confirm.")
            messagebox.showinfo("Tenant Notified", msg)
            self.manage_result.configure(text="Date set & tenant notified!", text_color="green")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
```

---

## Step 4: Commit & Push

```bash
git add maintenance_manager.py views/maintenance_view.py
git commit -m "Sprint 2 (Numair): maintenance cost report (by apartment & city), date communication, tenant notification"
git push origin feature/maintenance-sprint2
```

Then:
1. Go to **GitHub** → click "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/maintenance-sprint2`
3. Title: `Sprint 2 (Numair): Maintenance cost reports and date communication`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review

---

## Quick Reference: Test Data After Seeding

After running `seed_db.py`, the following maintenance data exists:

| Ticket | Apartment | Description | Priority | Status | Staff | Cost | Hours |
|--------|-----------|-------------|----------|--------|-------|------|-------|
| 1 | 101 (Bristol) | Leaking kitchen tap | High | Fixed | maint1 | £150 | 2.5h |
| 2 | 201 (Cardiff) | Broken window latch | Medium | Fixed | maint1 | £75 | 1.0h |
| 3 | 101 (Bristol) | Flickering hallway light | Low | Open | — | — | — |

**What you should see in your Cost Report tab:**
- **Per-Apartment:** Unit 101 = 2 tickets, £150 total cost, 2.5h. Unit 201 = 1 ticket, £75 total, 1.0h.
- **Per-City:** Bristol = 2 tickets, £150 total. Cardiff = 1 ticket, £75 total.
- **Summary Cards:** Total: 3, Fixed: 2, Open: 1

**Testing the Notify Tenant feature:**
1. Enter Ticket ID: `3` (the open flickering light ticket)
2. Enter Date: `2026-04-15`
3. Click "Set Date & Notify Tenant"
4. Expected: Success popup showing tenant John Smith's contact info
