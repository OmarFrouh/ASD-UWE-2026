# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from tests.test_base import BaseTest
from property_manager import PropertyManager
from auth_manager import AuthManager


class TestPropertyManagerV2(BaseTest):
    def setUp(self):
        super().setUp()
        self.prop = PropertyManager(self.db)
        self.auth = AuthManager(self.db)
        self.prop.add_apartment("1A", "High St", "900", "50", "Bristol", "2")
        self.apt_id = self.prop.get_all_apartments()[0][0]

    def _add_tenant(self, username="t1", apt_id=None):
        self.auth.create_user(username, "pass", "tenant")
        uid = self.db.fetch_one("SELECT id FROM users WHERE username=?", (username,))[0]
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent, apartment_id)"
            " VALUES (?,?,?,?,?,?)",
            (uid, "AB123456C", "Alice", "Active", 900, apt_id or self.apt_id))
        self.db.execute_query(
            "UPDATE apartments SET status='Occupied' WHERE id=?", (apt_id or self.apt_id,))
        return uid

    # ── delete_apartment ──────────────────────────────────────────────────────

    def test_delete_vacant_apartment(self):
        self.prop.delete_apartment(self.apt_id)
        row = self.db.fetch_one(
            "SELECT id FROM apartments WHERE id=?", (self.apt_id,))
        self.assertIsNone(row)

    def test_delete_occupied_apartment_raises(self):
        self._add_tenant()
        with self.assertRaises(Exception) as ctx:
            self.prop.delete_apartment(self.apt_id)
        self.assertIn("active tenant", str(ctx.exception).lower())

    def test_delete_nonexistent_apartment_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.prop.delete_apartment(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    # ── get_apartment_detail ──────────────────────────────────────────────────

    def test_detail_vacant_returns_empty_tenant_fields(self):
        d = self.prop.get_apartment_detail(self.apt_id)
        self.assertEqual(d["unit_number"], "1A")
        self.assertIsNone(d["tenant_name"])
        self.assertEqual(d["maintenance_count"], 0)

    def test_detail_with_tenant_returns_tenant_fields(self):
        self._add_tenant()
        d = self.prop.get_apartment_detail(self.apt_id)
        self.assertEqual(d["tenant_name"], "Alice")
        self.assertAlmostEqual(d["tenant_rent"], 900.0)

    def test_detail_nonexistent_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.prop.get_apartment_detail(9999)
        self.assertIn("not found", str(ctx.exception).lower())

    def test_detail_includes_maintenance_count(self):
        self.db.execute_query(
            "INSERT INTO maintenance_requests (apartment_id, description, priority, status, date_reported)"
            " VALUES (?,?,?,?,?)",
            (self.apt_id, "Leaking tap", "Low", "Open", "2025-01-01"))
        d = self.prop.get_apartment_detail(self.apt_id)
        self.assertEqual(d["maintenance_count"], 1)


if __name__ == "__main__":
    unittest.main()
