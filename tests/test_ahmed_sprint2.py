# Student Name: Omar Alfrouh
# Student ID: 24020879

"""
Comprehensive tests for Ahmed's Sprint 2 work.
Tests cover:
  - InvoiceManager: get_overdue_with_details(), get_invoice_aging()
  - PaymentManager: get_collected_vs_pending(), get_payment_history_by_method(), get_monthly_revenue()
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tests.test_base import BaseTest
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager


class AhmedTestBase(BaseTest):
    """Shared setup for Ahmed's Sprint 2 test classes."""

    def setUp(self):
        super().setUp()
        # Seed a user, apartment, and active tenant
        self.db.execute_query(
            "INSERT INTO users (id, username, password_hash, role) VALUES (100, 'testtenant', 'hash', 'front_desk')"
        )
        self.db.execute_query(
            "INSERT INTO apartments (id, unit_number, address, city, number_of_rooms, rental_price, status) "
            "VALUES (10, 'A1', '1 Test St', 'Bristol', 2, 800.00, 'Vacant')"
        )
        self.db.execute_query(
            """INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email, occupation,
               apartment_id, monthly_rent, status, lease_start_date, lease_end_date)
               VALUES (100, 'AB123456C', 'Test Tenant', '07700000001', 'test@test.com',
                       'Teacher', 10, 800.00, 'Active', '2026-01-01', '2027-01-01')"""
        )

    def _insert_overdue_invoice(self, iid=1, uid=100, days_ago=10):
        past = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        issued = (datetime.now() - timedelta(days=days_ago + 30)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,800.00,'Pending')", (iid, uid, issued, past)
        )

    def _insert_future_invoice(self, iid=2, uid=100):
        future = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,800.00,'Pending')", (iid, uid, today, future)
        )

    def _insert_paid_past_invoice(self, iid=3, uid=100):
        past = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        issued = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,800.00,'Paid')", (iid, uid, issued, past)
        )


# ════════════════════════════════════════════════════════════════════════════
# InvoiceManager — get_overdue_with_details
# ════════════════════════════════════════════════════════════════════════════
class TestOverdueWithDetails(AhmedTestBase):
    def setUp(self):
        super().setUp()
        self.im = InvoiceManager(self.db)

    def test_returns_overdue_invoice(self):
        """Overdue pending invoice should be returned."""
        self._insert_overdue_invoice()
        rows = self.im.get_overdue_with_details()
        self.assertEqual(len(rows), 1)

    def test_returns_correct_7_fields(self):
        """Each row must have exactly 7 fields per the docstring."""
        self._insert_overdue_invoice()
        row = self.im.get_overdue_with_details()[0]
        self.assertEqual(len(row), 7)

    def test_correct_tenant_name(self):
        self._insert_overdue_invoice()
        row = self.im.get_overdue_with_details()[0]
        self.assertEqual(row[1], "Test Tenant")

    def test_correct_email(self):
        self._insert_overdue_invoice()
        row = self.im.get_overdue_with_details()[0]
        self.assertEqual(row[2], "test@test.com")

    def test_correct_phone(self):
        self._insert_overdue_invoice()
        row = self.im.get_overdue_with_details()[0]
        self.assertEqual(row[3], "07700000001")

    def test_days_overdue_is_positive(self):
        self._insert_overdue_invoice(days_ago=15)
        row = self.im.get_overdue_with_details()[0]
        self.assertGreater(row[6], 0)

    def test_excludes_paid_invoices(self):
        """Paid past-due invoices must NOT appear."""
        self._insert_paid_past_invoice()
        self.assertEqual(len(self.im.get_overdue_with_details()), 0)

    def test_excludes_future_invoices(self):
        """Invoices not yet due must NOT appear."""
        self._insert_future_invoice()
        self.assertEqual(len(self.im.get_overdue_with_details()), 0)

    def test_empty_when_no_invoices(self):
        self.assertEqual(self.im.get_overdue_with_details(), [])

    def test_sorted_most_overdue_first(self):
        """Invoice overdue by 60 days should appear before one overdue by 5."""
        self._insert_overdue_invoice(iid=1, days_ago=60)
        self._insert_overdue_invoice(iid=2, days_ago=5)
        rows = self.im.get_overdue_with_details()
        self.assertGreater(rows[0][6], rows[1][6])


# ════════════════════════════════════════════════════════════════════════════
# InvoiceManager — get_invoice_aging
# ════════════════════════════════════════════════════════════════════════════
class TestInvoiceAging(AhmedTestBase):
    def setUp(self):
        super().setUp()
        self.im = InvoiceManager(self.db)

    def test_returns_dict(self):
        self._insert_overdue_invoice()
        self.assertIsInstance(self.im.get_invoice_aging(), dict)

    def test_empty_when_no_overdue(self):
        self.assertEqual(self.im.get_invoice_aging(), {})

    def test_0_30_bucket(self):
        """Invoice 10 days overdue should land in '0-30 days'."""
        self._insert_overdue_invoice(days_ago=10)
        result = self.im.get_invoice_aging()
        self.assertIn("0-30 days", result)
        self.assertEqual(result["0-30 days"], 1)

    def test_excludes_future_invoices(self):
        self._insert_future_invoice()
        self.assertEqual(self.im.get_invoice_aging(), {})

    def test_excludes_paid_invoices(self):
        self._insert_paid_past_invoice()
        self.assertEqual(self.im.get_invoice_aging(), {})

    def test_bucket_values_are_integers(self):
        self._insert_overdue_invoice()
        for val in self.im.get_invoice_aging().values():
            self.assertIsInstance(val, int)


# ════════════════════════════════════════════════════════════════════════════
# PaymentManager — get_collected_vs_pending
# ════════════════════════════════════════════════════════════════════════════
class TestCollectedVsPending(AhmedTestBase):
    def setUp(self):
        super().setUp()
        self.pm = PaymentManager(self.db)
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (1, 100, '2026-01-01', '2026-02-01', 800.00, 'Pending')"
        )

    def test_returns_dict(self):
        self.assertIsInstance(self.pm.get_collected_vs_pending(), dict)

    def test_has_required_keys(self):
        result = self.pm.get_collected_vs_pending()
        for key in ("collected", "pending", "total"):
            self.assertIn(key, result)

    def test_zero_collected_no_payments(self):
        self.assertEqual(self.pm.get_collected_vs_pending()["collected"], 0.0)

    def test_pending_equals_invoice_total(self):
        self.assertEqual(self.pm.get_collected_vs_pending()["pending"], 800.00)

    def test_total_equals_all_invoices(self):
        self.assertEqual(self.pm.get_collected_vs_pending()["total"], 800.00)

    def test_collected_after_full_payment(self):
        self.pm.record_payment(1, 800.00, "Card", "T1")
        self.assertEqual(self.pm.get_collected_vs_pending()["collected"], 800.00)

    def test_pending_drops_after_full_payment(self):
        self.pm.record_payment(1, 800.00, "Card", "T1")
        self.assertEqual(self.pm.get_collected_vs_pending()["pending"], 0.0)

    def test_total_includes_paid_invoices(self):
        """total should count every invoice, regardless of status."""
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (2, 100, '2026-01-01', '2026-02-01', 500.00, 'Paid')"
        )
        self.assertEqual(self.pm.get_collected_vs_pending()["total"], 1300.00)

    def test_partial_payment_updates_collected(self):
        """A partial payment should be reflected in collected."""
        self.pm.record_payment(1, 300.00, "Cash", "T1")
        result = self.pm.get_collected_vs_pending()
        self.assertEqual(result["collected"], 300.00)
        # Invoice is still Pending (partially paid)
        self.assertEqual(result["pending"], 800.00)


# ════════════════════════════════════════════════════════════════════════════
# PaymentManager — get_payment_history_by_method
# ════════════════════════════════════════════════════════════════════════════
class TestPaymentHistoryByMethod(AhmedTestBase):
    def setUp(self):
        super().setUp()
        self.pm = PaymentManager(self.db)
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (1, 100, '2026-01-01', '2026-03-01', 1000.00, 'Pending')"
        )

    def test_returns_list(self):
        self.assertIsInstance(self.pm.get_payment_history_by_method(), list)

    def test_empty_when_no_payments(self):
        self.assertEqual(self.pm.get_payment_history_by_method(), [])

    def test_row_has_3_fields(self):
        """Each row: (method, total_amount, count)."""
        self.pm.record_payment(1, 100.00, "Card", "T1")
        row = self.pm.get_payment_history_by_method()[0]
        self.assertEqual(len(row), 3)

    def test_method_name_correct(self):
        self.pm.record_payment(1, 100.00, "Card", "T1")
        methods = [r[0] for r in self.pm.get_payment_history_by_method()]
        self.assertIn("Card", methods)

    def test_total_amount_correct(self):
        self.pm.record_payment(1, 200.00, "Card", "T1")
        card = next(r for r in self.pm.get_payment_history_by_method() if r[0] == "Card")
        self.assertEqual(card[1], 200.00)

    def test_count_correct_with_multiple_payments(self):
        self.pm.record_payment(1, 50.00, "Cash", "T1")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (2, 100, '2026-01-01', '2026-04-01', 200.00, 'Pending')"
        )
        self.pm.record_payment(2, 50.00, "Cash", "T2")
        cash = next(r for r in self.pm.get_payment_history_by_method() if r[0] == "Cash")
        self.assertEqual(cash[2], 2)

    def test_multiple_methods_grouped(self):
        self.pm.record_payment(1, 300.00, "Card", "T1")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (2, 100, '2026-01-01', '2026-04-01', 500.00, 'Pending')"
        )
        self.pm.record_payment(2, 500.00, "Bank Transfer", "T2")
        methods = [r[0] for r in self.pm.get_payment_history_by_method()]
        self.assertIn("Card", methods)
        self.assertIn("Bank Transfer", methods)

    def test_sorted_by_total_desc(self):
        """Higher total should appear first per ORDER BY total DESC."""
        self.pm.record_payment(1, 100.00, "Cash", "T1")
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (2, 100, '2026-01-01', '2026-04-01', 500.00, 'Pending')"
        )
        self.pm.record_payment(2, 500.00, "Card", "T2")
        result = self.pm.get_payment_history_by_method()
        self.assertGreaterEqual(result[0][1], result[1][1])


# ════════════════════════════════════════════════════════════════════════════
# PaymentManager — get_monthly_revenue
# ════════════════════════════════════════════════════════════════════════════
class TestMonthlyRevenue(AhmedTestBase):
    def setUp(self):
        super().setUp()
        self.pm = PaymentManager(self.db)
        self.db.execute_query(
            "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (1, 100, '2026-01-01', '2026-03-01', 800.00, 'Pending')"
        )

    def test_returns_list(self):
        self.assertIsInstance(self.pm.get_monthly_revenue(), list)

    def test_empty_when_no_payments(self):
        self.assertEqual(self.pm.get_monthly_revenue(), [])

    def test_row_has_2_fields(self):
        """Each row: (month_label, total_amount)."""
        self.pm.record_payment(1, 800.00, "Card", "T1")
        row = self.pm.get_monthly_revenue()[0]
        self.assertEqual(len(row), 2)

    def test_month_format_yyyy_mm(self):
        self.pm.record_payment(1, 800.00, "Card", "T1")
        import re
        self.assertRegex(self.pm.get_monthly_revenue()[0][0], r"^\d{4}-\d{2}$")

    def test_total_correct(self):
        self.pm.record_payment(1, 800.00, "Card", "T1")
        self.assertEqual(self.pm.get_monthly_revenue()[0][1], 800.00)

    def test_capped_at_6_months(self):
        """LIMIT 6 in the query should cap results."""
        for i in range(1, 9):
            inv_id = 10 + i
            self.db.execute_query(
                "INSERT INTO invoices (id, tenant_id, issue_date, due_date, total_amount, status) "
                f"VALUES ({inv_id}, 100, '2026-01-01', '2026-03-01', 100.00, 'Pending')"
            )
            self.pm.record_payment(inv_id, 100.00, "Cash", f"T{i}")
        self.assertLessEqual(len(self.pm.get_monthly_revenue()), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
