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

        # Reject overpayment: check remaining balance
        existing = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id=?", (invoice_id,))
        already_paid = existing[0] if existing else 0
        remaining = invoice[0] - already_paid
        if amount > remaining:
            raise Exception(f"Amount exceeds remaining balance of {remaining:.2f}")

        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO payments (invoice_id, amount, payment_date, method, transaction_ref)
                VALUES (?, ?, ?, ?, ?)
            """, (invoice_id, amount, today, method, transaction_ref))
            payment_id = cursor.lastrowid

            # Check within same transaction if now fully paid
            cursor.execute("SELECT SUM(amount) FROM payments WHERE invoice_id=?", (invoice_id,))
            total_paid = cursor.fetchone()
            if total_paid and total_paid[0] >= invoice[0]:
                cursor.execute("UPDATE invoices SET status='Paid' WHERE id=?", (invoice_id,))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return payment_id

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

    def get_receipt_data(self, payment_id):
        """Returns formatted receipt data for a payment.
        Brief: 'generating the billing/dues receipts'
        Returns: dict with all fields needed for a receipt popup."""
        row = self.db_manager.fetch_one("""
            SELECT p.id, p.amount, p.payment_date, p.method, p.transaction_ref,
                   i.id, i.total_amount, i.issue_date, i.due_date, i.status,
                   t.full_name, t.ni_number, t.email, t.phone_number,
                   a.unit_number, a.address, a.city
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.id
            JOIN tenants t ON i.tenant_id = t.user_id
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE p.id=?
        """, (payment_id,))
        if not row:
            raise Exception("Payment not found")
        return {
            "payment_id": row[0],
            "amount": row[1],
            "payment_date": row[2],
            "method": row[3],
            "reference": row[4] or "N/A",
            "invoice_id": row[5],
            "invoice_total": row[6],
            "issue_date": row[7],
            "due_date": row[8],
            "invoice_status": row[9],
            "tenant_name": row[10],
            "ni_number": row[11],
            "email": row[12] or "N/A",
            "phone": row[13] or "N/A",
            "unit": row[14] or "N/A",
            "address": row[15] or "N/A",
            "city": row[16] or "N/A",
        }