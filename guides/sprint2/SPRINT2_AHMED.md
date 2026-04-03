# 🔵 SPRINT 2 GUIDE — AHMED DERAZ (Finance Lead)
**Role**: Financial Summary + Late Payment Notifications + Overdue Badges
**Prerequisite**: Omar must push Sprint 2 foundation first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Financial Summary Report, Late Payment Notification, Overdue Badges)
2. **Move cards on Project Board**: Drag your Sprint 2 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue

---

## Step 1: Setup (Read `guides/sprint2/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/finance-sprint2
source venv/bin/activate
pip install -r requirements.txt
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py    # confirm the Sprint 2 foundation loads
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/finance-sprint2 && git merge dev`

---

## Step 2: Update `invoice_manager.py`

Open `invoice_manager.py` and **add these new methods** at the bottom of the `InvoiceManager` class:

```python
    def get_overdue_with_details(self):
        """Returns overdue invoices with days overdue and tenant contact info.
        Used for late payment notification generation.
        Returns: list of (invoice_id, tenant_name, email, phone, due_date, amount, days_overdue)"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, t.email, t.phone_number, i.due_date, i.total_amount,
                   CAST(julianday(?) - julianday(i.due_date) AS INTEGER) AS days_overdue
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.user_id
            WHERE i.status = 'Pending' AND i.due_date < ?
            ORDER BY days_overdue DESC
        """, (today, today))

    def get_invoice_aging(self):
        """Returns invoice aging breakdown (0-30 days, 31-60, 61-90, 90+).
        Returns: dict of age_bracket -> count"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        rows = self.db_manager.fetch_all("""
            SELECT
                CASE
                    WHEN julianday(?) - julianday(i.due_date) <= 30 THEN '0-30 days'
                    WHEN julianday(?) - julianday(i.due_date) <= 60 THEN '31-60 days'
                    WHEN julianday(?) - julianday(i.due_date) <= 90 THEN '61-90 days'
                    ELSE '90+ days'
                END AS age_bracket,
                COUNT(*) AS cnt
            FROM invoices i
            WHERE i.status = 'Pending' AND i.due_date < ?
            GROUP BY age_bracket
            ORDER BY age_bracket
        """, (today, today, today, today))
        return {row[0]: row[1] for row in rows}
```

---

## Step 3: Update `payment_manager.py`

Open `payment_manager.py` and **add these new methods** at the bottom of the `PaymentManager` class:

```python
    def get_collected_vs_pending(self):
        """Returns collected vs pending rent totals for financial summary.
        Returns: dict with collected, pending, total keys"""
        collected = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(amount), 0) FROM payments")[0]
        pending = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'Pending'")[0]
        total = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices")[0]
        return {"collected": collected, "pending": pending, "total": total}

    def get_payment_history_by_method(self):
        """Returns payment totals grouped by payment method.
        Returns: list of (method, total_amount, count)"""
        return self.db_manager.fetch_all("""
            SELECT method, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt
            FROM payments
            GROUP BY method
            ORDER BY total DESC
        """)

    def get_monthly_revenue(self):
        """Returns monthly revenue for the last 6 months.
        Returns: list of (month_label, total_collected)"""
        return self.db_manager.fetch_all("""
            SELECT strftime('%Y-%m', payment_date) AS month,
                   COALESCE(SUM(amount), 0) AS total
            FROM payments
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        """)
```

---

## Step 4: Update `views/invoice_view.py`

You need to add **overdue notification badges** to the invoice list. Replace the entire `refresh` method with this updated version:

```python
    def refresh(self):
        # ─── All Invoices Tab ───
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.get_all_invoices():
            # Add visual overdue tag
            status_display = inv[5]
            if inv[5] == "Pending":
                from datetime import datetime
                try:
                    due = datetime.strptime(inv[3], "%Y-%m-%d")
                    if due < datetime.now():
                        status_display = "⚠️ OVERDUE"
                except (ValueError, TypeError):
                    pass
            self.inv_tree.insert("", "end", values=(
                inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", status_display))

        # ─── Overdue Tab ───
        for item in self.od_tree.get_children():
            self.od_tree.delete(item)
        for od in self.invoice_manager.get_overdue_invoices():
            self.od_tree.insert("", "end", values=(
                od[0], od[1], od[2], f"£{od[3]:.2f}"))

        # ─── Late Payment Notification Tab ───
        if hasattr(self, 'notif_tree'):
            for item in self.notif_tree.get_children():
                self.notif_tree.delete(item)
            for row in self.invoice_manager.get_overdue_with_details():
                # invoice_id, name, email, phone, due_date, amount, days_overdue
                self.notif_tree.insert("", "end", values=(
                    row[0], row[1], row[2] or "N/A", row[3] or "N/A",
                    row[4], f"£{row[5]:.2f}", f"{row[6]} days"))
```

Now, in the `__init__` method, **add a new tab** after the overdue tab. Find the line:
```python
        tab_overdue = self.tabview.add("Overdue")
```

And **add these lines after it**:

```python
        tab_notif = self.tabview.add("Late Notifications")
```

Then after `self.refresh()` is called at the end of `__init__`, **add the Late Notifications tab build code**. Add this new method to the class and call it from `__init__`:

```python
    def build_notification_tab(self, tab):
        """Builds the Late Payment Notification tab with tenant contact info."""
        from views.ui_helpers import setup_treeview_scroll

        ctk.CTkLabel(tab, text="⚠️ Late Payment Notifications",
                     font=("Arial", 16, "bold"), text_color="orange").pack(pady=(10, 5))
        ctk.CTkLabel(tab, text="These tenants have overdue invoices. Contact them for payment.",
                     font=("Arial", 12), text_color="gray").pack(pady=(0, 10))

        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Invoice", "Tenant", "Email", "Phone", "Due Date", "Amount", "Days Overdue")
        self.notif_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)
        for c in cols:
            self.notif_tree.heading(c, text=c)
            self.notif_tree.column(c, width=100)
```

In `__init__`, call the new method **before** `self.refresh()`:

```python
        # Add this line before self.refresh()
        self.build_notification_tab(tab_notif)
        self.refresh()
```

---

## Step 5: Update `views/payment_view.py`

Add a **"Financial Summary"** tab to the payment view. In `__init__`, after the existing tabs, add:

```python
        tab_summary = self.tabview.add("Financial Summary")
```

Then add this new method to the class:

```python
    def build_summary_tab(self, tab):
        """Builds the Financial Summary tab showing collected vs pending."""
        from views.ui_helpers import setup_treeview_scroll

        # Summary cards
        self.sum_card_frame = ctk.CTkFrame(tab)
        self.sum_card_frame.pack(fill="x", padx=10, pady=10)

        # Payment method breakdown
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Payment Method", "Total Amount", "Transaction Count")
        self.sum_tree = setup_treeview_scroll(tree_frame, columns=cols, height=8)
        for c in cols:
            self.sum_tree.heading(c, text=c)
            self.sum_tree.column(c, width=150)

    def refresh_summary(self):
        """Refreshes the Financial Summary tab data."""
        if not hasattr(self, 'sum_card_frame'):
            return

        # Summary cards
        for w in self.sum_card_frame.winfo_children():
            w.destroy()
        summary = self.payment_manager.get_collected_vs_pending()
        cards = [
            ("Collected", f"£{summary['collected']:.2f}"),
            ("Pending", f"£{summary['pending']:.2f}"),
            ("Total Invoiced", f"£{summary['total']:.2f}"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.sum_card_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=15, pady=10, sticky="nsew")
            self.sum_card_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 28, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Payment method breakdown
        for item in self.sum_tree.get_children():
            self.sum_tree.delete(item)
        for row in self.payment_manager.get_payment_history_by_method():
            self.sum_tree.insert("", "end", values=(row[0], f"£{row[1]:.2f}", row[2]))
```

Call these in `__init__`:

```python
        # Add after the existing tab setup, BEFORE self.refresh()
        self.build_summary_tab(tab_summary)
        self.refresh()
```

And update the existing `refresh` method to also call `self.refresh_summary()`:

```python
    def refresh(self):
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(
                p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))
        self.refresh_summary()
```

---

## Step 6: Commit & Push

```bash
git add invoice_manager.py payment_manager.py views/invoice_view.py views/payment_view.py
git commit -m "Sprint 2 (Ahmed): financial summary, late payment notifications, overdue badges, payment method breakdown"
git push origin feature/finance-sprint2
```

Then:
1. Go to **GitHub** → click "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/finance-sprint2`
3. Title: `Sprint 2 (Ahmed): Financial summary and late payment notifications`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review

---

## Quick Reference: Test Data After Seeding

After running `seed_db.py`, the following test data exists:

| Invoice ID | Tenant | Amount | Status | Due Date | Overdue? |
|------------|--------|--------|--------|----------|----------|
| 1 | John Smith | £850 | Pending | ~5 days ago | ✅ YES |
| 2 | John Smith | £850 | Pending | ~25 days from now | ❌ No |
| 3 | Sarah Jones | £1100 | Paid | ~5 days ago | ❌ No (paid) |
| 4 | Sarah Jones | £1100 | Pending | ~25 days from now | ❌ No |

**What you should see:**
- Invoice ID 1 should show "⚠️ OVERDUE" in the All Invoices tab
- Late Notifications tab should show 1 row (John Smith, Invoice 1)
- Financial Summary should show £1100 collected, £2800 pending
