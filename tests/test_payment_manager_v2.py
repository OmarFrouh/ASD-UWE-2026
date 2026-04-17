# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from payment_manager import PaymentManager
from invoice_manager import InvoiceManager
from auth_manager import AuthManager
from property_manager import PropertyManager


class TestPaymentManagerV2(BaseTest):
    def setUp(self):
        super().setUp()
        self.pay  = PaymentManager(self.db)
        self.inv  = InvoiceManager(self.db)
        self.auth = AuthManager(self.db)
        self.prop = PropertyManager(self.db)
        self._fixtures()

    def _fixtures(self):
        self.auth.create_user("u1", "pass", "tenant")
        self.u1 = self.db.fetch_one("SELECT id FROM users WHERE username='u1'")[0]
        self.prop.add_apartment("1A", "High St", "900", "50", "Bristol", "2")
        self.apt = self.prop.get_all_apartments()[0][0]
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent, apartment_id)"
            " VALUES (?,?,?,?,?,?)",
            (self.u1, "AB123456C", "Alice", "Active", 900, self.apt))
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status)"
            " VALUES (?,?,?,?,'Pending')",
            (self.u1, "2025-01-01", future, 900))
        self.inv_id = self.db.fetch_one("SELECT id FROM invoices")[0]

    def _record(self, amount=900, method="Card"):
        return self.pay.record_payment(self.inv_id, amount, method)

    # ── void_payment ──────────────────────────────────────────────────────────

    def test_void_payment_removes_row(self):
        pid = self._record()
        self.pay.void_payment(pid)
        row = self.db.fetch_one("SELECT id FROM payments WHERE id=?", (pid,))
        self.assertIsNone(row)

    def test_void_payment_reverts_invoice_to_pending(self):
        pid = self._record(900)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Paid")
        self.pay.void_payment(pid)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Pending")

    def test_void_partial_payment_invoice_stays_pending(self):
        pid = self._record(500)
        self.pay.void_payment(pid)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Pending")

    def test_void_one_of_two_payments_keeps_invoice_paid(self):
        pid1 = self._record(450)
        pid2 = self._record(450)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Paid")
        self.pay.void_payment(pid1)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Pending")

    def test_void_nonexistent_payment_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.pay.void_payment(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── get_payments_for_tenant ───────────────────────────────────────────────

    def test_get_payments_for_tenant_returns_rows(self):
        self._record()
        rows = self.pay.get_payments_for_tenant(self.u1)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0][1], 900.0)

    def test_get_payments_for_tenant_empty(self):
        rows = self.pay.get_payments_for_tenant(self.u1)
        self.assertEqual(rows, [])

    def test_get_payments_for_tenant_multiple(self):
        future = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status)"
            " VALUES (?,?,?,?,'Pending')",
            (self.u1, "2025-02-01", future, 500))
        inv2 = self.db.fetch_one(
            "SELECT id FROM invoices WHERE total_amount=500")[0]
        self.pay.record_payment(self.inv_id, 900, "Cash")
        self.pay.record_payment(inv2, 500, "Card")
        rows = self.pay.get_payments_for_tenant(self.u1)
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
