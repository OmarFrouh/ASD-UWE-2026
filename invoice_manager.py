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