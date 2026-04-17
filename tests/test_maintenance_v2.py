# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from tests.test_base import BaseTest
from maintenance_manager import MaintenanceManager
from invoice_manager import InvoiceManager
from auth_manager import AuthManager
from property_manager import PropertyManager


class TestMaintenanceV2(BaseTest):
    def setUp(self):
        super().setUp()
        self.mm   = MaintenanceManager(self.db)
        self.auth = AuthManager(self.db)
        self.prop = PropertyManager(self.db)
        self._fixtures()

    def _fixtures(self):
        self.prop.add_apartment("1A", "High St", "900", "50", "Bristol", "2")
        self.apt_id = self.prop.get_all_apartments()[0][0]
        self.auth.create_user("t1", "pass", "tenant")
        self.t1 = self.db.fetch_one("SELECT id FROM users WHERE username='t1'")[0]
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent, apartment_id)"
            " VALUES (?,?,?,?,?,?)",
            (self.t1, "AB123456C", "Alice", "Active", 900, self.apt_id))
        self.auth.create_user("staff1", "pass", "maintenance",
                              employee_id="EMP001", department="Maintenance")
        self.staff1 = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")[0]
        self.mm.create_ticket(self.apt_id, self.t1, "Leaking tap", "Low")
        self.ticket_id = self.db.fetch_one(
            "SELECT id FROM maintenance_requests")[0]

    # ── delete_ticket ─────────────────────────────────────────────────────────

    def test_delete_open_ticket(self):
        self.mm.delete_ticket(self.ticket_id)
        row = self.db.fetch_one(
            "SELECT id FROM maintenance_requests WHERE id=?", (self.ticket_id,))
        self.assertIsNone(row)

    def test_delete_assigned_ticket(self):
        self.mm.assign_staff(self.ticket_id, self.staff1)
        self.mm.delete_ticket(self.ticket_id)
        row = self.db.fetch_one(
            "SELECT id FROM maintenance_requests WHERE id=?", (self.ticket_id,))
        self.assertIsNone(row)

    def test_delete_in_progress_raises(self):
        self.mm.assign_staff(self.ticket_id, self.staff1)
        self.mm.update_status(self.ticket_id, "In Progress")
        with self.assertRaises(Exception) as ctx:
            self.mm.delete_ticket(self.ticket_id)
        self.assertIn("in progress", str(ctx.exception).lower())

    def test_delete_fixed_raises(self):
        self.mm.assign_staff(self.ticket_id, self.staff1)
        self.mm.update_status(self.ticket_id, "In Progress")
        self.mm.update_status(self.ticket_id, "Fixed")
        with self.assertRaises(Exception) as ctx:
            self.mm.delete_ticket(self.ticket_id)
        self.assertIn("fixed", str(ctx.exception).lower())

    def test_delete_closed_raises(self):
        self.mm.assign_staff(self.ticket_id, self.staff1)
        self.mm.update_status(self.ticket_id, "In Progress")
        self.mm.update_status(self.ticket_id, "Fixed")
        self.mm.update_status(self.ticket_id, "Closed")
        with self.assertRaises(Exception) as ctx:
            self.mm.delete_ticket(self.ticket_id)
        self.assertIn("closed", str(ctx.exception).lower())

    def test_delete_nonexistent_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.mm.delete_ticket(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── get_ticket_detail ─────────────────────────────────────────────────────

    def test_detail_contains_all_keys(self):
        d = self.mm.get_ticket_detail(self.ticket_id)
        for key in ("id", "unit_number", "address", "city", "tenant_name",
                    "tenant_phone", "description", "priority", "status",
                    "date_reported", "scheduled_date", "date_resolved",
                    "time_spent", "cost", "assigned_staff"):
            self.assertIn(key, d, f"Missing key: {key}")

    def test_detail_correct_values(self):
        d = self.mm.get_ticket_detail(self.ticket_id)
        self.assertEqual(d["id"],          self.ticket_id)
        self.assertEqual(d["unit_number"], "1A")
        self.assertEqual(d["tenant_name"], "Alice")
        self.assertEqual(d["description"], "Leaking tap")
        self.assertEqual(d["priority"],    "Low")
        self.assertEqual(d["status"],      "Open")

    def test_detail_nonexistent_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.mm.get_ticket_detail(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── get_tickets_for_tenant ────────────────────────────────────────────────

    def test_tickets_for_tenant_returns_rows(self):
        rows = self.mm.get_tickets_for_tenant(self.t1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], self.ticket_id)

    def test_tickets_for_tenant_empty(self):
        self.auth.create_user("t2", "pass", "tenant")
        t2 = self.db.fetch_one("SELECT id FROM users WHERE username='t2'")[0]
        rows = self.mm.get_tickets_for_tenant(t2)
        self.assertEqual(rows, [])

    def test_tickets_for_tenant_multiple(self):
        self.mm.create_ticket(self.apt_id, self.t1, "Broken light", "Medium")
        rows = self.mm.get_tickets_for_tenant(self.t1)
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
