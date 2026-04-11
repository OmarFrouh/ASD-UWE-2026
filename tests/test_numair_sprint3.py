# Student Name: Numair
# Student ID: 24026758

import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from tenant_manager import TenantManager
import bcrypt


def _make_hash(pw="pass123"):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())


class TestComplaintEdgeCases(BaseTest):
    """Edge-case tests for the complaint logging system."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant2", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, status)
            VALUES (1, 'NI111111A', 'Tenant One', 'Active')
        """)
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, status)
            VALUES (2, 'NI222222B', 'Tenant Two', 'Active')
        """)

    def test_multiple_complaints_same_tenant(self):
        """A tenant can have multiple open complaints."""
        self.tm.log_complaint(1, "Issue A", "First problem")
        self.tm.log_complaint(1, "Issue B", "Second problem")
        self.tm.log_complaint(1, "Issue C", "Third problem")
        complaints = self.tm.get_complaints_for_tenant(1)
        self.assertEqual(len(complaints), 3)

    def test_complaints_isolated_between_tenants(self):
        """Tenant 1's complaints don't appear for Tenant 2."""
        self.tm.log_complaint(1, "Issue A", "Tenant 1 problem")
        self.tm.log_complaint(2, "Issue B", "Tenant 2 problem")
        self.assertEqual(len(self.tm.get_complaints_for_tenant(1)), 1)
        self.assertEqual(len(self.tm.get_complaints_for_tenant(2)), 1)

    def test_get_all_complaints_returns_both_tenants(self):
        self.tm.log_complaint(1, "Issue A", "Details A")
        self.tm.log_complaint(2, "Issue B", "Details B")
        all_c = self.tm.get_all_complaints()
        self.assertEqual(len(all_c), 2)
        names = [c[1] for c in all_c]
        self.assertIn("Tenant One", names)
        self.assertIn("Tenant Two", names)

    def test_complaint_for_terminated_tenant(self):
        """Can still log complaints for terminated tenants (they may have existing issues)."""
        self.db.execute_query("UPDATE tenants SET status='Terminated' WHERE user_id=1")
        # The tenant still exists, just terminated — complaints should still work
        # because the brief says "tracking associated... complaint logs"
        result = self.tm.log_complaint(1, "Past Issue", "Problem from before termination")
        self.assertTrue(result)

    def test_complaint_date_is_set(self):
        self.tm.log_complaint(1, "Test", "Details")
        complaints = self.tm.get_complaints_for_tenant(1)
        self.assertIsNotNone(complaints[0][1])  # date_logged

    def test_resolve_only_changes_target_complaint(self):
        """Resolving one complaint doesn't affect others."""
        self.tm.log_complaint(1, "Issue A", "Details A")
        self.tm.log_complaint(1, "Issue B", "Details B")
        complaints = self.tm.get_complaints_for_tenant(1)
        # Resolve only the first one
        self.tm.resolve_complaint(complaints[0][0])
        updated = self.tm.get_complaints_for_tenant(1)
        resolved_count = sum(1 for c in updated if c[4] == "Resolved")
        open_count = sum(1 for c in updated if c[4] == "Open")
        self.assertEqual(resolved_count, 1)
        self.assertEqual(open_count, 1)

    def test_complaint_resolved_date_is_today(self):
        self.tm.log_complaint(1, "Test", "Details")
        complaints = self.tm.get_complaints_for_tenant(1)
        self.tm.resolve_complaint(complaints[0][0])
        updated = self.tm.get_complaints_for_tenant(1)
        self.assertEqual(updated[0][5], datetime.now().strftime("%Y-%m-%d"))


class TestUpdateTenantEdgeCases(BaseTest):
    """Edge-case tests for the update tenant feature."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("tenant1", _make_hash(), "tenant"))
        self.db.execute_query("""
            INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email, status)
            VALUES (1, 'NI111111A', 'Test Tenant', '07700000000', 'test@test.com', 'Active')
        """)

    def test_update_single_field_only(self):
        """Updating just email should not affect phone."""
        self.tm.update_tenant(1, email="new@email.com")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[4], "new@email.com")
        self.assertEqual(t[3], "07700000000")  # phone unchanged

    def test_update_all_fields_at_once(self):
        self.tm.update_tenant(1,
            full_name="New Name", phone="07799999999", email="new@test.com",
            occupation="Doctor", references="Dr. New", emergency_contact="New Contact",
            apt_requirements="3 bed house")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[2], "New Name")
        self.assertEqual(t[3], "07799999999")
        self.assertEqual(t[4], "new@test.com")
        self.assertEqual(t[5], "Doctor")
        self.assertEqual(t[6], "Dr. New")
        self.assertEqual(t[7], "New Contact")
        self.assertEqual(t[8], "3 bed house")

    def test_update_to_empty_string(self):
        """Updating a field to empty string should work (clears the field)."""
        self.tm.update_tenant(1, phone="")
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(t[3], "")

    def test_get_tenant_by_id_returns_all_fields(self):
        t = self.tm.get_tenant_by_id(1)
        self.assertEqual(len(t), 15)  # 15 columns
        self.assertEqual(t[0], 1)      # user_id
        self.assertEqual(t[1], "NI111111A")  # ni_number
        self.assertEqual(t[14], "Active")    # status


class TestEarlyTerminationNoticeEdgeCases(BaseTest):
    """Edge-case tests for the 1-month notice period."""

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
            INSERT INTO tenants (user_id, ni_number, full_name, monthly_rent, apartment_id, status)
            VALUES (1, 'NI111111A', 'Test Tenant', 850.00, 1, 'Active')
        """)

    def test_already_terminated_fails(self):
        self.tm.early_termination(1)
        with self.assertRaises(Exception) as ctx:
            self.tm.early_termination(1)
        self.assertIn("already Terminated", str(ctx.exception))

    def test_archived_tenant_fails(self):
        self.db.execute_query("UPDATE tenants SET status='Archived' WHERE user_id=1")
        with self.assertRaises(Exception) as ctx:
            self.tm.early_termination(1)
        self.assertIn("already Archived", str(ctx.exception))

    def test_nonexistent_tenant_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.early_termination(999)
        self.assertIn("not found", str(ctx.exception))

    def test_return_type_is_dict(self):
        result = self.tm.early_termination(1)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["penalty"], float)
        self.assertIsInstance(result["effective_date"], str)

    def test_effective_date_is_30_days_from_today(self):
        """Notice period effective date must be exactly 30 days from today."""
        result = self.tm.early_termination(1)
        expected = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(result["effective_date"], expected)


if __name__ == "__main__":
    unittest.main()
