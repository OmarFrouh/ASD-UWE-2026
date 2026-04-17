# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
import os
import tempfile
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from invoice_manager import InvoiceManager
from auth_manager import AuthManager
from property_manager import PropertyManager
from views.pdf_generator import generate_invoice_pdf


class TestInvoicePdfData(BaseTest):
    def setUp(self):
        super().setUp()
        self.inv  = InvoiceManager(self.db)
        self.auth = AuthManager(self.db)
        self.prop = PropertyManager(self.db)
        self._setup_fixtures()

    def _setup_fixtures(self):
        self.auth.create_user("u1", "pass", "tenant")
        self.u1_id = self.db.fetch_one("SELECT id FROM users WHERE username='u1'")[0]

        self.prop.add_apartment("10A", "1 Park Lane", "1200", "600", "Bristol", "2")
        self.apt_id = self.prop.get_all_apartments()[0][0]

        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, email, phone_number, "
            "status, monthly_rent, apartment_id) VALUES (?,?,?,?,?,?,?,?)",
            (self.u1_id, "AB123456C", "Alice Smith", "alice@example.com",
             "07700900000", "Active", 900, self.apt_id))
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Pending')",
            (self.u1_id, "2025-01-01", future, 900))
        self.inv_id = self.db.fetch_one("SELECT id FROM invoices")[0]

    # ── get_invoice_pdf_data ──────────────────────────────────────────────────

    def test_pdf_data_contains_all_keys(self):
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        for key in ("invoice_id", "issue_date", "due_date", "total_amount", "status",
                    "tenant_name", "ni_number", "email", "phone",
                    "unit", "address", "city", "payments"):
            self.assertIn(key, data, f"Missing key: {key}")

    def test_pdf_data_correct_values(self):
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        self.assertEqual(data["invoice_id"],   self.inv_id)
        self.assertEqual(data["tenant_name"],  "Alice Smith")
        self.assertEqual(data["ni_number"],    "AB123456C")
        self.assertEqual(data["email"],        "alice@example.com")
        self.assertEqual(data["phone"],        "07700900000")
        self.assertEqual(data["unit"],         "10A")
        self.assertEqual(data["address"],      "1 Park Lane")
        self.assertEqual(data["city"],         "Bristol")
        self.assertAlmostEqual(data["total_amount"], 900.0)
        self.assertEqual(data["status"],       "Pending")

    def test_pdf_data_no_payments_initially(self):
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        self.assertEqual(data["payments"], [])

    def test_pdf_data_includes_payments(self):
        self.db.execute_query(
            "INSERT INTO payments (invoice_id, amount, payment_date, method) "
            "VALUES (?,?,?,?)",
            (self.inv_id, 900, "2025-01-10", "Card"))
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        self.assertEqual(len(data["payments"]), 1)
        self.assertAlmostEqual(data["payments"][0][0], 900.0)
        self.assertEqual(data["payments"][0][2], "Card")

    def test_pdf_data_nonexistent_invoice_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.inv.get_invoice_pdf_data(9999)
        self.assertIn("not found", str(ctx.exception))

    def test_pdf_data_no_apartment_returns_empty_strings(self):
        self.auth.create_user("u2", "pass", "tenant")
        u2 = self.db.fetch_one("SELECT id FROM users WHERE username='u2'")[0]
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent) "
            "VALUES (?,?,?,?,?)", (u2, "ZZ999999Z", "Bob No-Apt", "Active", 500))
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Pending')",
            (u2, "2025-01-01", "2025-02-01", 500))
        inv2 = self.db.fetch_one(
            "SELECT id FROM invoices WHERE tenant_id=?", (u2,))[0]
        data = self.inv.get_invoice_pdf_data(inv2)
        self.assertEqual(data["unit"],    "")
        self.assertEqual(data["address"], "")
        self.assertEqual(data["city"],    "")

    # ── generate_invoice_pdf ──────────────────────────────────────────────────

    def test_pdf_file_created(self):
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            generate_invoice_pdf(data, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)

    def test_pdf_is_valid_pdf_header(self):
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            generate_invoice_pdf(data, path)
            with open(path, "rb") as f:
                header = f.read(4)
            self.assertEqual(header, b"%PDF")
        finally:
            os.unlink(path)

    def test_pdf_with_payments(self):
        self.db.execute_query(
            "INSERT INTO payments (invoice_id, amount, payment_date, method, transaction_ref) "
            "VALUES (?,?,?,?,?)",
            (self.inv_id, 900, "2025-01-10", "Bank Transfer", "TXN001"))
        data = self.inv.get_invoice_pdf_data(self.inv_id)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            generate_invoice_pdf(data, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 1000)
        finally:
            os.unlink(path)

    def test_pdf_with_no_apartment_data(self):
        self.auth.create_user("u3", "pass", "tenant")
        u3 = self.db.fetch_one("SELECT id FROM users WHERE username='u3'")[0]
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent) "
            "VALUES (?,?,?,?,?)", (u3, "XX123456X", "Charlie Plain", "Active", 750))
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?,?,?,?,'Paid')", (u3, "2025-01-01", "2025-02-01", 750))
        inv3 = self.db.fetch_one("SELECT id FROM invoices WHERE tenant_id=?", (u3,))[0]
        data = self.inv.get_invoice_pdf_data(inv3)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            generate_invoice_pdf(data, path)
            self.assertTrue(os.path.exists(path))
        finally:
            os.unlink(path)
