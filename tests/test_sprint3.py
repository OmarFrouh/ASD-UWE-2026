# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from tenant_manager import TenantManager
from payment_manager import PaymentManager
import bcrypt


def _make_hash(pw="pass123"):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())


# ═══════════════════════════════════════════════════════════════
# 1. UPDATE TENANT RECORDS
# ═══════════════════════════════════════════════════════════════

class TestUpdateTenant(BaseTest):
    """Tests for tenant_manager.update_tenant() — Sprint 3 brief gap."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email,
                occupation, references_info, emergency_contact, apartment_requirements, status)
            VALUES (1, 'NI111111A', 'Test Tenant', '07700000000', 'test@test.com',
                'Engineer', 'Dr. Adams', 'Jane Doe', '2 bed flat', 'Active')
        """)

    def test_update_name(self):
        self.tm.update_tenant(1, full_name="Updated Name")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[2], "Updated Name")

    def test_update_multiple_fields(self):
        self.tm.update_tenant(1, phone="07799999999", email="new@test.com", occupation="Teacher")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[3], "07799999999")
        self.assertEqual(t[4], "new@test.com")
        self.assertEqual(t[5], "Teacher")

    def test_update_preserves_unchanged_fields(self):
        self.tm.update_tenant(1, phone="07799999999")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[2], "Test Tenant")    # name unchanged
        self.assertEqual(t[4], "test@test.com")  # email unchanged
        self.assertEqual(t[3], "07799999999")    # phone updated

    def test_update_terminated_tenant_fails(self):
        self.db.execute_query("UPDATE tenants SET status='Terminated' WHERE user_id=1")
        with self.assertRaises(Exception) as ctx:
            self.tm.update_tenant(1, full_name="New Name")
        self.assertIn("Terminated", str(ctx.exception))

    def test_update_archived_tenant_fails(self):
        self.db.execute_query("UPDATE tenants SET status='Archived' WHERE user_id=1")
        with self.assertRaises(Exception) as ctx:
            self.tm.update_tenant(1, full_name="New Name")
        self.assertIn("Archived", str(ctx.exception))

    def test_update_nonexistent_tenant_fails(self):
        with self.assertRaises(Exception):
            self.tm.update_tenant(999, full_name="Nobody")

    def test_update_no_fields_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.update_tenant(1)
        self.assertIn("No fields", str(ctx.exception))

    def test_get_tenant_by_id(self):
        t = self.tm.get_tenant_by_id(1)
        self.assertIsNotNone(t)
        self.assertEqual(t[0], 1)
        self.assertEqual(t[1], "NI111111A")
        self.assertEqual(t[2], "Test Tenant")

    def test_get_tenant_by_id_not_found(self):
        t = self.tm.get_tenant_by_id(999)
        self.assertIsNone(t)


# ═══════════════════════════════════════════════════════════════
# 2. EARLY TERMINATION — 1-MONTH NOTICE PERIOD
# ═══════════════════════════════════════════════════════════════

class TestEarlyTerminationNotice(BaseTest):
    """Tests for the 1-month notice period enforcement in early_termination()."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO apartments (unit_number, address, city, rental_price, square_footage, status)
            VALUES ('101', '10 Park St', 'Bristol', 850, 650, 'Occupied')
        """)
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, monthly_rent, apartment_id,
                lease_start_date, lease_end_date, status)
            VALUES (1, 'NI111111A', 'Test Tenant', 850.00, 1, '2025-01-01', '2026-12-01', 'Active')
        """)

    def test_returns_dict_with_penalty_and_date(self):
        result = self.tm.early_termination(1)
        self.assertIsInstance(result, dict)
        self.assertIn("penalty", result)
        self.assertIn("effective_date", result)

    def test_penalty_is_five_percent(self):
        result = self.tm.early_termination(1)
        self.assertAlmostEqual(result["penalty"], 42.50, places=2)

    def test_effective_date_is_30_days_from_now(self):
        result = self.tm.early_termination(1)
        expected = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(result["effective_date"], expected)

    def test_tenant_becomes_terminated(self):
        self.tm.early_termination(1)
        tenant = self.db.fetch_one("SELECT status FROM tenants WHERE user_id=1")
        self.assertEqual(tenant[0], "Terminated")

    def test_apartment_becomes_vacant(self):
        self.tm.early_termination(1)
        apt = self.db.fetch_one("SELECT status FROM apartments WHERE id=1")
        self.assertEqual(apt[0], "Vacant")

    def test_lease_end_set_to_effective_date(self):
        result = self.tm.early_termination(1)
        tenant = self.db.fetch_one("SELECT lease_end_date FROM tenants WHERE user_id=1")
        self.assertEqual(tenant[0], result["effective_date"])

    def test_no_rent_penalty_is_zero(self):
        self.db.execute_query("UPDATE tenants SET monthly_rent=NULL WHERE user_id=1")
        result = self.tm.early_termination(1)
        self.assertEqual(result["penalty"], 0)


# ═══════════════════════════════════════════════════════════════
# 3. COMPLAINT LOGS
# ═══════════════════════════════════════════════════════════════

class TestComplaintLogs(BaseTest):
    """Tests for complaint logging, retrieval, and resolution."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, status)
            VALUES (1, 'NI111111A', 'Test Tenant', 'Active')
        """)

    def test_log_complaint_success(self):
        result = self.tm.log_complaint(1, "Noise", "Loud music at night")
        self.assertTrue(result)

    def test_log_complaint_nonexistent_tenant(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.log_complaint(999, "Test", "Test description")
        self.assertIn("Tenant not found", str(ctx.exception))

    def test_log_complaint_empty_subject(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.log_complaint(1, "", "Description here")
        self.assertIn("required", str(ctx.exception))

    def test_log_complaint_empty_description(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.log_complaint(1, "Subject here", "")
        self.assertIn("required", str(ctx.exception))

    def test_get_complaints_for_tenant(self):
        self.tm.log_complaint(1, "Issue 1", "Details 1")
        self.tm.log_complaint(1, "Issue 2", "Details 2")
        complaints = self.tm.get_complaints_for_tenant(1)
        self.assertEqual(len(complaints), 2)

    def test_get_complaints_empty_for_no_complaints(self):
        complaints = self.tm.get_complaints_for_tenant(1)
        self.assertEqual(len(complaints), 0)

    def test_get_all_complaints_includes_tenant_name(self):
        self.tm.log_complaint(1, "Issue", "Details")
        all_c = self.tm.get_all_complaints()
        self.assertEqual(len(all_c), 1)
        self.assertEqual(all_c[0][1], "Test Tenant")

    def test_resolve_complaint(self):
        self.tm.log_complaint(1, "Issue", "Details")
        complaints = self.tm.get_complaints_for_tenant(1)
        cid = complaints[0][0]
        result = self.tm.resolve_complaint(cid)
        self.assertTrue(result)
        updated = self.tm.get_complaints_for_tenant(1)
        self.assertEqual(updated[0][4], "Resolved")

    def test_resolve_sets_resolved_date(self):
        self.tm.log_complaint(1, "Issue", "Details")
        complaints = self.tm.get_complaints_for_tenant(1)
        cid = complaints[0][0]
        self.tm.resolve_complaint(cid)
        updated = self.tm.get_complaints_for_tenant(1)
        self.assertIsNotNone(updated[0][5])  # resolved_date

    def test_resolve_already_resolved_fails(self):
        self.tm.log_complaint(1, "Issue", "Details")
        complaints = self.tm.get_complaints_for_tenant(1)
        cid = complaints[0][0]
        self.tm.resolve_complaint(cid)
        with self.assertRaises(Exception) as ctx:
            self.tm.resolve_complaint(cid)
        self.assertIn("already resolved", str(ctx.exception))

    def test_resolve_nonexistent_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.resolve_complaint(999)
        self.assertIn("not found", str(ctx.exception))


# ═══════════════════════════════════════════════════════════════
# 4. BILLING / DUES RECEIPTS
# ═══════════════════════════════════════════════════════════════

class TestBillingReceipt(BaseTest):
    """Tests for payment receipt generation."""

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
        self.db.execute_query("""
            INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status)
            VALUES (1, '2026-04-01', '2026-05-01', 850.00, 'Pending')
        """)

    def test_record_payment_returns_payment_id(self):
        result = self.pm.record_payment(1, 850.00, "Card")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_get_receipt_data_all_fields(self):
        pid = self.pm.record_payment(1, 850.00, "Card", "TXN-TEST")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["tenant_name"], "Test Tenant")
        self.assertEqual(receipt["amount"], 850.00)
        self.assertEqual(receipt["method"], "Card")
        self.assertEqual(receipt["reference"], "TXN-TEST")
        self.assertEqual(receipt["invoice_id"], 1)
        self.assertEqual(receipt["invoice_total"], 850.00)
        self.assertEqual(receipt["unit"], "101")
        self.assertEqual(receipt["city"], "Bristol")

    def test_receipt_not_found(self):
        with self.assertRaises(Exception) as ctx:
            self.pm.get_receipt_data(999)
        self.assertIn("not found", str(ctx.exception))

    def test_receipt_after_partial_payment(self):
        self.db.execute_query("UPDATE invoices SET total_amount=1000 WHERE id=1")
        pid = self.pm.record_payment(1, 500.00, "Cash")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["amount"], 500.00)
        self.assertEqual(receipt["invoice_total"], 1000.00)
        self.assertEqual(receipt["invoice_status"], "Pending")

    def test_receipt_no_reference(self):
        pid = self.pm.record_payment(1, 850.00, "Cash")
        receipt = self.pm.get_receipt_data(pid)
        self.assertEqual(receipt["reference"], "N/A")


if __name__ == "__main__":
    unittest.main()
