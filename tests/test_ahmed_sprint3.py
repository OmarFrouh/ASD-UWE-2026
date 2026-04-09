# Student Name: Ahmed Deraz
# Student ID: 24046227

import unittest
from tests.test_base import BaseTest
from payment_manager import PaymentManager
import bcrypt


def _make_hash(pw="pass123"):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())


class TestReceiptEdgeCases(BaseTest):
    """Additional edge-case tests for receipt generation."""

    def setUp(self):
        super().setUp()
        self.pm = PaymentManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO apartments (unit_number, address, city, rental_price, square_footage, status)
            VALUES ('101', '10 Park St', 'Bristol', 850, 650, 'Occupied')
        """)
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, email, phone_number,
                apartment_id, monthly_rent, status)
            VALUES (1, 'NI111111A', 'Test Tenant', 'test@test.com', '07700000000', 1, 850, 'Active')
        """)

    def _create_invoice(self, amount=850.00, status="Pending"):
        self.db.execute_query("""
            INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status)
            VALUES (1, '2026-04-01', '2026-05-01', ?, ?)
        """, (amount, status))

    def test_receipt_with_bank_transfer(self):
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Bank Transfer", "TXN-BT001")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["method"], "Bank Transfer")
        self.assertEqual(receipt["reference"], "TXN-BT001")

    def test_receipt_with_cash_no_ref(self):
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Cash")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["method"], "Cash")
        self.assertEqual(receipt["reference"], "N/A")

    def test_receipt_partial_payment_shows_pending(self):
        self._create_invoice(amount=1000)
        pid = self.pm.record_payment(1, 500, "Card")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["amount"], 500)
        self.assertEqual(receipt["invoice_total"], 1000)
        self.assertEqual(receipt["invoice_status"], "Pending")

    def test_receipt_full_payment_shows_paid(self):
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Card")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["invoice_status"], "Paid")

    def test_receipt_tenant_no_apartment(self):
        """Tenant without apartment — receipt should show N/A for property fields."""
        self.db.execute_query("UPDATE tenants SET apartment_id=NULL WHERE user_id=1")
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Card")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["unit"], "N/A")
        self.assertEqual(receipt["address"], "N/A")

    def test_receipt_includes_dates(self):
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Card")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["issue_date"], "2026-04-01")
        self.assertEqual(receipt["due_date"], "2026-05-01")
        self.assertIsNotNone(receipt["payment_date"])

    def test_record_payment_returns_positive_int(self):
        self._create_invoice()
        pid = self.pm.record_payment(1, 850, "Card")
        self.assertIsInstance(pid, int)
        self.assertGreater(pid, 0)

    def test_multiple_payments_different_receipts(self):
        self._create_invoice(amount=1000)
        pid1 = self.pm.record_payment(1, 400, "Card")
        pid2 = self.pm.record_payment(1, 600, "Cash")
        r1 = self.pm.get_receipt_data(pid1)
        r2 = self.pm.get_receipt_data(pid2)
        self.assertNotEqual(r1["payment_id"], r2["payment_id"])
        self.assertEqual(r1["amount"], 400)
        self.assertEqual(r2["amount"], 600)


if __name__ == "__main__":
    unittest.main()
