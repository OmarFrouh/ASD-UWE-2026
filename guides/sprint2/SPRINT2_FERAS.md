# 🟡 SPRINT 2 GUIDE — FERAS BADER (Frontend Lead)
**Role**: Tenant Search/Filter + Notification Display
**Prerequisite**: Omar must push Sprint 2 foundation first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Search Tenants, Filter by Status, Display Notifications)
2. **Move cards on Project Board**: Drag your Sprint 2 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue

---

## Step 1: Setup (Read `guides/sprint2/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/tenant-sprint2
source venv/bin/activate
pip install -r requirements.txt
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py    # confirm the Sprint 2 foundation loads
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/tenant-sprint2 && git merge dev`

---

## Step 2: Update `tenant_manager.py`

Open `tenant_manager.py` and **add these new methods** at the bottom of the `TenantManager` class (before the final closing of the class):

```python
    def search_tenants(self, query):
        """Search tenants by name, NI number, email, or phone.
        Returns: list matching the same format as get_all_tenants()"""
        search = f"%{query}%"
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
              AND (t.full_name LIKE ? OR t.ni_number LIKE ? OR t.email LIKE ? OR t.phone_number LIKE ?)
            ORDER BY t.full_name
        """, (search, search, search, search))

    def filter_tenants_by_status(self, status):
        """Filter tenants by status (Active, Archived, Terminated, All).
        Returns: list matching the same format as get_all_tenants()"""
        if status == "All":
            return self.db_manager.fetch_all("""
                SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                       t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                       t.monthly_rent, t.status, a.unit_number
                FROM tenants t
                LEFT JOIN apartments a ON t.apartment_id = a.id
                ORDER BY t.full_name
            """)
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = ?
            ORDER BY t.full_name
        """, (status,))

    def get_tenant_count_by_status(self):
        """Returns dict with counts per status for dashboard display."""
        rows = self.db_manager.fetch_all("""
            SELECT status, COUNT(*) FROM tenants GROUP BY status
        """)
        return {row[0]: row[1] for row in rows}
```

---

## Step 3: Update `views/tenant_view.py`

You need to add a **search bar** and **status filter dropdown** to the "Active Tenants" tab. Replace the entire `build_list_tab` method with:

```python
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

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_filter.set("Active")
        self.refresh_list()
```

Then **replace the entire `refresh_list` method** with:

```python
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
```

---

## Step 4: Commit & Push

```bash
git add tenant_manager.py views/tenant_view.py
git commit -m "Sprint 2 (Feras): tenant search, filter by status, summary bar"
git push origin feature/tenant-sprint2
```

Then:
1. Go to **GitHub** → you'll see a yellow banner "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/tenant-sprint2`
3. Title: `Sprint 2 (Feras): Tenant search, filter, and notification display`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review
