# 🔵 SPRINT 1 GUIDE — AHMED DERAZ (Finance Lead)
**Role**: Invoice & Payment Module
**Prerequisite**: Omar must push his changes first! Pull before starting.

## Step 0: Project Management (Before Coding)

1. **Go to GitHub Issues**: Create issues for your tasks (Generate Invoice, Record Payment, Track Late Payments)
2. **Move cards on Project Board**: Drag your Sprint 1 items to "In Progress"
3. **Update `BACKLOG.md`**: Mark your items as `[In Progress]` and commit
4. **After finishing**: Move cards to "Done", mark `[x]` in backlog, write a short comment on each Issue

---

## Step 1: Setup (Read `guides/GIT_WORKFLOW.md` first!)

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/finance-module
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Every time you sit down to code**, run: `git checkout dev && git pull origin dev && git checkout feature/finance-module && git merge dev`

---

## Step 2: Create `invoice_manager.py` (project root)

```python
# Student Name: Ahmed Deraz
# Student ID: [YOUR_ID]

from datetime import datetime, timedelta

class InvoiceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_invoice(self, tenant_id, amount=None):
        tenant = self.db_manager.fetch_one(
            "SELECT monthly_rent, full_name FROM tenants WHERE user_id=?", (tenant_id,))
        if not tenant:
            raise Exception("Tenant not found")

        if amount is None:
            amount = tenant[0]
        if not amount or amount <= 0:
            raise Exception("Invalid amount")

        today = datetime.now().strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        self.db_manager.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,'Pending')",
            (tenant_id, today, due, amount))
        return True

    def get_all_invoices(self):
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, i.issue_date, i.due_date, i.total_amount, i.status
            FROM invoices i JOIN tenants t ON i.tenant_id = t.user_id
            ORDER BY i.issue_date DESC
        """)

    def get_overdue_invoices(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, i.due_date, i.total_amount
            FROM invoices i JOIN tenants t ON i.tenant_id = t.user_id
            WHERE i.status = 'Pending' AND i.due_date < ?
            ORDER BY i.due_date
        """, (today,))

    def mark_paid(self, invoice_id):
        self.db_manager.execute_query(
            "UPDATE invoices SET status='Paid' WHERE id=?", (invoice_id,))
```

---

## Step 3: Create `payment_manager.py` (project root)

```python
# Student Name: Ahmed Deraz
# Student ID: [YOUR_ID]

from datetime import datetime

class PaymentManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def record_payment(self, invoice_id, amount, method, transaction_ref=""):
        invoice = self.db_manager.fetch_one(
            "SELECT total_amount, status FROM invoices WHERE id=?", (invoice_id,))
        if not invoice:
            raise Exception("Invoice not found")
        if invoice[1] == "Paid":
            raise Exception("Invoice already paid")

        amount = float(amount)
        if amount <= 0:
            raise Exception("Amount must be positive")

        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db_manager.execute_query("""
            INSERT INTO payments (invoice_id, amount, payment_date, method, transaction_ref)
            VALUES (?, ?, ?, ?, ?)
        """, (invoice_id, amount, today, method, transaction_ref))

        # Check if fully paid
        total_paid = self.db_manager.fetch_one(
            "SELECT SUM(amount) FROM payments WHERE invoice_id=?", (invoice_id,))
        if total_paid and total_paid[0] >= invoice[0]:
            self.db_manager.execute_query(
                "UPDATE invoices SET status='Paid' WHERE id=?", (invoice_id,))

        return True

    def get_all_payments(self):
        return self.db_manager.fetch_all("""
            SELECT p.id, t.full_name, p.amount, p.payment_date, p.method, p.transaction_ref, i.id
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.id
            JOIN tenants t ON i.tenant_id = t.user_id
            ORDER BY p.payment_date DESC
        """)

    def get_financial_summary(self):
        collected = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(amount),0) FROM payments")
        pending = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount),0) FROM invoices WHERE status='Pending'")
        return {
            "Collected": collected[0] if collected else 0,
            "Pending": pending[0] if pending else 0,
        }
```

---

## Step 4: Create `views/invoice_view.py`

```python
# Student Name: Ahmed Deraz
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk
from invoice_manager import InvoiceManager

class InvoiceView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.invoice_manager = InvoiceManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="💰 Invoice Management", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_gen = self.tabview.add("Generate Invoice")
        tab_list = self.tabview.add("All Invoices")
        tab_overdue = self.tabview.add("Overdue")

        # Generate Tab
        gen_frame = ctk.CTkFrame(tab_gen)
        gen_frame.pack(pady=30, padx=40)

        ctk.CTkLabel(gen_frame, text="Tenant ID:").grid(row=0, column=0, padx=10, pady=10)
        self.tenant_id_entry = ctk.CTkEntry(gen_frame, width=200)
        self.tenant_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(gen_frame, text="Amount (optional):").grid(row=1, column=0, padx=10, pady=10)
        self.amount_entry = ctk.CTkEntry(gen_frame, width=200, placeholder_text="Uses monthly rent if blank")
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkButton(gen_frame, text="Generate Invoice", command=self.generate, width=250).grid(
            row=2, column=0, columnspan=2, pady=20)

        # All Invoices Tab
        cols = ("ID", "Tenant", "Issued", "Due", "Amount", "Status")
        self.inv_tree = ttk.Treeview(tab_list, columns=cols, show="headings", height=15)
        for c in cols:
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=110)
        self.inv_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Overdue Tab
        od_cols = ("ID", "Tenant", "Due Date", "Amount")
        self.od_tree = ttk.Treeview(tab_overdue, columns=od_cols, show="headings", height=15)
        for c in od_cols:
            self.od_tree.heading(c, text=c)
            self.od_tree.column(c, width=130)
        self.od_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh()

    def generate(self):
        tid = self.tenant_id_entry.get()
        amt = self.amount_entry.get()
        if not tid:
            messagebox.showwarning("Error", "Enter tenant ID.")
            return
        try:
            self.invoice_manager.generate_invoice(int(tid), float(amt) if amt else None)
            messagebox.showinfo("Success", "Invoice generated!")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.get_all_invoices():
            self.inv_tree.insert("", "end", values=(inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", inv[5]))

        for item in self.od_tree.get_children():
            self.od_tree.delete(item)
        for od in self.invoice_manager.get_overdue_invoices():
            self.od_tree.insert("", "end", values=(od[0], od[1], od[2], f"£{od[3]:.2f}"))
```

---

## Step 5: Create `views/payment_view.py`

```python
# Student Name: Ahmed Deraz
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox, ttk
from payment_manager import PaymentManager

class PaymentView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.payment_manager = PaymentManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="💳 Payment Processing", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_record = self.tabview.add("Record Payment")
        tab_history = self.tabview.add("Payment History")

        # Record Tab
        rec_frame = ctk.CTkFrame(tab_record)
        rec_frame.pack(pady=30, padx=40)

        ctk.CTkLabel(rec_frame, text="Invoice ID:").grid(row=0, column=0, padx=10, pady=8)
        self.inv_id_entry = ctk.CTkEntry(rec_frame, width=200)
        self.inv_id_entry.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(rec_frame, text="Amount (£):").grid(row=1, column=0, padx=10, pady=8)
        self.pay_amount_entry = ctk.CTkEntry(rec_frame, width=200)
        self.pay_amount_entry.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkLabel(rec_frame, text="Method:").grid(row=2, column=0, padx=10, pady=8)
        self.method_combo = ctk.CTkComboBox(rec_frame, values=["Card", "Cash", "Bank Transfer"], width=200)
        self.method_combo.grid(row=2, column=1, padx=10, pady=8)
        self.method_combo.set("Card")

        ctk.CTkLabel(rec_frame, text="Reference:").grid(row=3, column=0, padx=10, pady=8)
        self.ref_entry = ctk.CTkEntry(rec_frame, width=200, placeholder_text="Optional")
        self.ref_entry.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkButton(rec_frame, text="Record Payment", command=self.record, width=250).grid(
            row=4, column=0, columnspan=2, pady=20)

        # History Tab
        cols = ("ID", "Tenant", "Amount", "Date", "Method", "Ref", "Invoice")
        self.pay_tree = ttk.Treeview(tab_history, columns=cols, show="headings", height=15)
        for c in cols:
            self.pay_tree.heading(c, text=c)
            self.pay_tree.column(c, width=100)
        self.pay_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def record(self):
        inv_id = self.inv_id_entry.get()
        amount = self.pay_amount_entry.get()
        method = self.method_combo.get()
        ref = self.ref_entry.get()

        if not inv_id or not amount:
            messagebox.showwarning("Error", "Invoice ID and Amount required.")
            return
        try:
            self.payment_manager.record_payment(int(inv_id), amount, method, ref)
            messagebox.showinfo("Success", "Payment recorded!")
            for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
                e.delete(0, 'end')
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))
```

---

## Step 6: Commit & Push

```bash
git add -A
git commit -m "Sprint 1 (Ahmed): Invoice generation, payment processing, overdue tracking"
git push origin feature/finance-module
```

Then:
1. Go to **GitHub** → click "Compare & pull request"
2. Set **base: `dev`** ← compare: `feature/finance-module`
3. Title: `Sprint 1 (Ahmed): Invoice and payment module`
4. Assign **Omar** as reviewer
5. Click **Create pull request**
6. **DO NOT merge it yourself** — wait for Omar's review
