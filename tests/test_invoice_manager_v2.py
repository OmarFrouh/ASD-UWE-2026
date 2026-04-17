# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager
from auth_manager import AuthManager
from property_manager import PropertyManager


class TestInvoiceManagerV2(BaseTest):
    def setUp(self):
        super().setUp()
        self.inv  = InvoiceManager(self.db)
        self.pay  = PaymentManager(self.db)
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

    # ── mark_paid guards ──────────────────────────────────────────────────────

    def test_mark_paid_pending_succeeds(self):
        self.inv.mark_paid(self.inv_id)
        status = self.db.fetch_one(
            "SELECT status FROM invoices WHERE id=?", (self.inv_id,))[0]
        self.assertEqual(status, "Paid")

    def test_mark_paid_already_paid_raises(self):
        self.inv.mark_paid(self.inv_id)
        with self.assertRaises(Exception) as ctx:
            self.inv.mark_paid(self.inv_id)
        self.assertIn("already paid", str(ctx.exception).lower())

    def test_mark_paid_nonexistent_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.inv.mark_paid(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── delete_invoice ────────────────────────────────────────────────────────

    def test_delete_pending_invoice_removes_row(self):
        self.inv.delete_invoice(self.inv_id)
        row = self.db.fetch_one("SELECT id FROM invoices WHERE id=?", (self.inv_id,))
        self.assertIsNone(row)

    def test_delete_paid_invoice_raises(self):
        self.inv.mark_paid(self.inv_id)
        with self.assertRaises(Exception) as ctx:
            self.inv.delete_invoice(self.inv_id)
        self.assertIn("paid", str(ctx.exception).lower())

    def test_delete_invoice_with_payments_raises(self):
        self.db.execute_query(
            "INSERT INTO payments (invoice_id, amount, payment_date, method) VALUES (?,?,?,?)",
            (self.inv_id, 500, "2025-01-10", "Card"))
        with self.assertRaises(Exception) as ctx:
            self.inv.delete_invoice(self.inv_id)
        self.assertIn("payment", str(ctx.exception).lower())

    def test_delete_nonexistent_invoice_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.inv.delete_invoice(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── get_invoices_for_tenant ───────────────────────────────────────────────

    def test_get_invoices_for_tenant_returns_rows(self):
        rows = self.inv.get_invoices_for_tenant(self.u1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], self.inv_id)

    def test_get_invoices_for_tenant_empty_for_unknown(self):
        rows = self.inv.get_invoices_for_tenant(9999)
        self.assertEqual(rows, [])

    def test_get_invoices_for_tenant_multiple(self):
        future = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status)"
            " VALUES (?,?,?,?,'Pending')",
            (self.u1, "2025-02-01", future, 900))
        rows = self.inv.get_invoices_for_tenant(self.u1)
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
