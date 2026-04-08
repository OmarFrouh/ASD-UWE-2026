import unittest
from tests.test_base import BaseTest
from tenant_manager import TenantManager
from property_manager import PropertyManager

class TestTenantManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.tenant = TenantManager(self.db)
        self.prop = PropertyManager(self.db)
        
        # Setup dummy apartment
        self.prop.add_apartment("T100", "Tenant Way", 1000, 500)
        apts = self.prop.get_all_apartments()
        self.apt_id = apts[0][0]

    def test_register_and_assign_tenant(self):
        self.tenant.register_tenant("user1", "pass", "NI123", "John Doe", "000", "e@e", "Dev", "Good", "Mom", "None")
        
        # Find user ID (it inserts sequentially from 1 usually in blank DBs, but let's query)
        users = self.db.fetch_all("SELECT id FROM users WHERE username='user1'")
        user_id = users[0][0]

        # Assign to apartment
        self.tenant.assign_apartment(user_id, self.apt_id, "2026-01-01", "2026-12-31", 1000.0, 500.0)
        
        # Verify apartment is Occupied
        apt = self.db.fetch_one("SELECT status FROM apartments WHERE id=?", (self.apt_id,))
        self.assertEqual(apt[0], "Occupied")

    def test_archive_tenant_clears_apartment_ghost(self):
        self.tenant.register_tenant("ghost", "pass", "NI999", "Ghost", "", "", "", "", "", "")
        user_id = self.db.fetch_one("SELECT id FROM users")[0]
        self.tenant.assign_apartment(user_id, self.apt_id, "2026-01-01", "2026-12-31", 1000.0, 500.0)
        
        # Archive the tenant
        self.tenant.archive_tenant(user_id)
        
        # Verify apartment is back to Vacant (fixes Ghosting bug)
        apt = self.db.fetch_one("SELECT status FROM apartments WHERE id=?", (self.apt_id,))
        self.assertEqual(apt[0], "Vacant")
        
        # Verify tenant is Archived and apartment_id is null
        t = self.db.fetch_one("SELECT status, apartment_id FROM tenants WHERE user_id=?", (user_id,))
        self.assertEqual(t[0], "Archived")
        self.assertIsNone(t[1])

    def test_early_termination_charges_penalty(self):
        self.tenant.register_tenant("pen", "pass", "NIPEN", "Pen", "", "", "", "", "", "")
        user_id = self.db.fetch_one("SELECT id FROM users")[0]
        self.tenant.assign_apartment(user_id, self.apt_id, "2026-01-01", "2026-12-31", 1000.0, 500.0)

        result = self.tenant.early_termination(user_id)
        # 5% of 1000 is 50
        self.assertEqual(result["penalty"], 50.0)

        t = self.db.fetch_one("SELECT status FROM tenants WHERE user_id=?", (user_id,))
        self.assertEqual(t[0], "Terminated")

        # Verify apartment is vacated
        apt = self.db.fetch_one("SELECT status FROM apartments WHERE id=?", (self.apt_id,))
        self.assertEqual(apt[0], "Vacant")

    def test_assign_occupied_apartment_fails(self):
        self.tenant.register_tenant("t1", "pass", "NI_A", "Tenant A", "", "", "", "", "", "")
        uid1 = self.db.fetch_all("SELECT id FROM users WHERE username='t1'")[0][0]
        self.tenant.assign_apartment(uid1, self.apt_id, "2026-01-01", "2026-12-31", 1000.0, 500.0)

        self.tenant.register_tenant("t2", "pass", "NI_B", "Tenant B", "", "", "", "", "", "")
        uid2 = self.db.fetch_all("SELECT id FROM users WHERE username='t2'")[0][0]

        with self.assertRaises(Exception) as ctx:
            self.tenant.assign_apartment(uid2, self.apt_id, "2026-01-01", "2026-12-31", 1000.0, 500.0)
        self.assertIn("already occupied", str(ctx.exception))
