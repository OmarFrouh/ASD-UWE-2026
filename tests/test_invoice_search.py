# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from invoice_manager import InvoiceManager
from auth_manager import AuthManager
from property_manager import PropertyManager
from tenant_manager import TenantManager


class TestInvoiceSearch(BaseTest):
    def setUp(self):
        super().setUp()
        self.inv  = InvoiceManager(self.db)
        self.auth = AuthManager(self.db)
        self.prop = PropertyManager(self.db)
        self.ten  = TenantManager(self.db)
        self._create_fixtures()

    def _create_fixtures(self):
        # Two tenants with invoices
        self.auth.create_user("u1", "pass", "tenant")
        self.auth.create_user("u2", "pass", "tenant")
        u1 = self.db.fetch_one("SELECT id FROM users WHERE username='u1'")[0]
        u2 = self.db.fetch_one("SELECT id FROM users WHERE username='u2'")[0]

        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent) "
            "VALUES (?,?,?,?,?)", (u1, "AA111111A", "Alice Smith", "Active", 900))
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent) "
            "VALUES (?,?,?,?,?)", (u2, "BB222222B", "Bob Jones", "Active", 800))

        today    = datetime.now().strftime("%Y-%m-%d")
        past_due = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        future   = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")

        # Alice: one Paid, one Pending (not overdue)
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Paid')", (u1, today, future, 900))
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Pending')", (u1, today, future, 900))

        # Bob: one Pending overdue
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Pending')", (u2, today, past_due, 800))

    def test_search_no_filter_returns_all(self):
        results = self.inv.search_invoices()
        self.assertEqual(len(results), 3)

    def test_filter_by_paid(self):
        results = self.inv.search_invoices(status="Paid")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Alice Smith")
        self.assertEqual(results[0][5], "Paid")

    def test_filter_by_pending(self):
        results = self.inv.search_invoices(status="Pending")
        self.assertEqual(len(results), 2)
        statuses = {r[5] for r in results}
        self.assertEqual(statuses, {"Pending"})

    def test_filter_by_overdue(self):
        results = self.inv.search_invoices(status="Overdue")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Bob Jones")

    def test_search_by_tenant_name(self):
        results = self.inv.search_invoices(tenant_name="Alice")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn("Alice", r[1])

    def test_search_case_insensitive(self):
        results = self.inv.search_invoices(tenant_name="alice")
        self.assertEqual(len(results), 2)

    def test_search_partial_name(self):
        results = self.inv.search_invoices(tenant_name="Jon")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Bob Jones")

    def test_combined_filter_status_and_name(self):
        results = self.inv.search_invoices(status="Paid", tenant_name="Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][5], "Paid")

    def test_combined_no_match_returns_empty(self):
        results = self.inv.search_invoices(status="Paid", tenant_name="Bob")
        self.assertEqual(len(results), 0)

    def test_search_nonexistent_name_returns_empty(self):
        results = self.inv.search_invoices(tenant_name="Nobody")
        self.assertEqual(len(results), 0)
