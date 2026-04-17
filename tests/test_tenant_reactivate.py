# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
from tests.test_base import BaseTest
from tenant_manager import TenantManager
from auth_manager import AuthManager


class TestTenantReactivate(BaseTest):
    def setUp(self):
        super().setUp()
        self.tm   = TenantManager(self.db)
        self.auth = AuthManager(self.db)
        self._make_tenant("alice", "Active")
        self._make_tenant("bob",   "Archived")
        self._make_tenant("carol", "Terminated")

    def _make_tenant(self, username, status):
        self.auth.create_user(username, "pass", "tenant")
        uid = self.db.fetch_one("SELECT id FROM users WHERE username=?", (username,))[0]
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status, monthly_rent)"
            " VALUES (?,?,?,?,?)",
            (uid, f"AB{uid:06d}C", username.title(), status, 800))
        setattr(self, f"uid_{username}", uid)

    def test_reactivate_archived_becomes_active(self):
        self.tm.reactivate_tenant(self.uid_bob)
        status = self.db.fetch_one(
            "SELECT status FROM tenants WHERE user_id=?", (self.uid_bob,))[0]
        self.assertEqual(status, "Active")

    def test_reactivate_terminated_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.reactivate_tenant(self.uid_carol)
        self.assertIn("terminated", str(ctx.exception).lower())

    def test_reactivate_already_active_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.reactivate_tenant(self.uid_alice)
        self.assertIn("already active", str(ctx.exception).lower())

    def test_reactivate_nonexistent_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.tm.reactivate_tenant(9999)
        self.assertIn("not found", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
