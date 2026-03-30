# Student Name: Ahmed Deraz
# Student ID: 24046227

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