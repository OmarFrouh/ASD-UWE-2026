# Student Name: Ahmed Deraz
# Student ID: 24046227

from datetime import datetime, timedelta

class InvoiceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_invoice(self, tenant_id, amount=None):
        tenant = self.db_manager.fetch_one(
            "SELECT monthly_rent, full_name, status FROM tenants WHERE user_id=?", (tenant_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[2] in ("Terminated", "Archived"):
            raise Exception(f"Cannot invoice a {tenant[2]} tenant")

        if amount is None:
            amount = tenant[0]
        if not amount or amount <= 0:
            raise Exception(
                "No monthly rent is set for this tenant. "
                "Assign them to an apartment first, or enter a custom amount manually."
            )

        today = datetime.now().strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        cursor = self.db_manager.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,'Pending')",
            (tenant_id, today, due, amount))
        return cursor.lastrowid if cursor else None

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
        inv = self.db_manager.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (invoice_id,))
        if not inv:
            raise Exception(f"Invoice {invoice_id} not found.")
        if inv[0] == "Paid":
            raise Exception("Invoice is already paid.")
        self.db_manager.execute_query(
            "UPDATE invoices SET status='Paid' WHERE id=?", (invoice_id,))

    def delete_invoice(self, invoice_id):
        inv = self.db_manager.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (invoice_id,))
        if not inv:
            raise Exception(f"Invoice {invoice_id} not found.")
        if inv[0] == "Paid":
            raise Exception("Cannot delete a paid invoice.")
        has_payments = self.db_manager.fetch_one(
            "SELECT COUNT(*) FROM payments WHERE invoice_id=?", (invoice_id,))
        if has_payments and has_payments[0] > 0:
            raise Exception("Cannot delete an invoice that has recorded payments.")
        self.db_manager.execute_query(
            "DELETE FROM invoices WHERE id=?", (invoice_id,))

    def get_invoices_for_tenant(self, tenant_id):
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, i.issue_date, i.due_date, i.total_amount, i.status
            FROM invoices i JOIN tenants t ON i.tenant_id = t.user_id
            WHERE i.tenant_id = ?
            ORDER BY i.issue_date DESC
        """, (tenant_id,))

    def get_payments_for_invoice(self, invoice_id):
        """Returns list of (payment_id, amount, payment_date) newest-first."""
        return self.db_manager.fetch_all(
            "SELECT id, amount, payment_date FROM payments "
            "WHERE invoice_id=? ORDER BY payment_date DESC",
            (invoice_id,))

    def get_invoice_pdf_data(self, invoice_id):
        row = self.db_manager.fetch_one("""
            SELECT i.id, i.issue_date, i.due_date, i.total_amount, i.status,
                   t.full_name, t.ni_number, t.email, t.phone_number,
                   COALESCE(a.unit_number, ''), COALESCE(a.address, ''),
                   COALESCE(a.city, '')
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.user_id
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE i.id = ?
        """, (invoice_id,))
        if not row:
            raise Exception(f"Invoice {invoice_id} not found.")
        payments = self.db_manager.fetch_all("""
            SELECT amount, payment_date, method, COALESCE(transaction_ref, '')
            FROM payments WHERE invoice_id = ?
            ORDER BY payment_date
        """, (invoice_id,))
        return {
            "invoice_id":   row[0],
            "issue_date":   row[1],
            "due_date":     row[2],
            "total_amount": row[3],
            "status":       row[4],
            "tenant_name":  row[5],
            "ni_number":    row[6],
            "email":        row[7] or "",
            "phone":        row[8] or "",
            "unit":         row[9],
            "address":      row[10],
            "city":         row[11],
            "payments":     payments,
        }

    def search_invoices(self, status=None, tenant_name=None):
        conditions, params = [], []
        today = datetime.now().strftime("%Y-%m-%d")
        if status == "Overdue":
            conditions.append("i.status = 'Pending' AND i.due_date < ?")
            params.append(today)
        elif status and status != "All":
            conditions.append("i.status = ?")
            params.append(status)
        if tenant_name and tenant_name.strip():
            conditions.append("t.full_name LIKE ?")
            params.append(f"%{tenant_name.strip()}%")
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        return self.db_manager.fetch_all(f"""
            SELECT i.id, t.full_name, i.issue_date, i.due_date, i.total_amount, i.status
            FROM invoices i JOIN tenants t ON i.tenant_id = t.user_id
            {where}
            ORDER BY i.issue_date DESC
        """, tuple(params))

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