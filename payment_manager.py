# Student Name: Ahmed Deraz
# Student ID: 24046227

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