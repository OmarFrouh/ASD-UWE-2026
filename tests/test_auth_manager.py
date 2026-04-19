# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
from tests.test_base import BaseTest
from auth_manager import AuthManager

class TestAuthManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.auth = AuthManager(self.db)

    def test_create_user_success(self):
        success = self.auth.create_user("omar", "secure123", "admin")
        self.assertTrue(success)

        # Verify login works
        user = self.auth.login("omar", "secure123")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "omar")
        self.assertEqual(user[3], "admin")

    def test_duplicate_username_fails(self):
        self.auth.create_user("feras", "pass", "staff", "EMP123")
        
        # Creating exact duplicate should throw exception handled in previous UI sweep
        with self.assertRaises(Exception) as context:
            self.auth.create_user("feras", "pass2", "tenant")
        self.assertIn("already taken", str(context.exception))

    def test_bad_login_fails(self):
        self.auth.create_user("ahmed", "correct", "tenant")
        user = self.auth.login("ahmed", "wrong")
        self.assertIsNone(user)
        
    def test_missing_employee_id_for_staff(self):
        # Staff require an employee ID, otherwise it rollbacks
        with self.assertRaises(Exception) as context:
            self.auth.create_user("new_staff", "pass", "manager")
        self.assertIn("Employee ID is required", str(context.exception))

    def test_invalid_role_rejected(self):
        with self.assertRaises(Exception) as ctx:
            self.auth.create_user("hacker", "pass", "super_admin")
        self.assertIn("Invalid role", str(ctx.exception))

    # ── delete_user tests ──────────────────────────────────────────────────────

    def test_delete_user_success(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("staff1", "pass", "manager", "EMP001", "Ops")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        staff = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")
        self.auth.delete_user(staff[0], admin[0])
        self.assertIsNone(self.auth.login("staff1", "pass"))
        remaining = self.db.fetch_one("SELECT id FROM users WHERE id=?", (staff[0],))
        self.assertIsNone(remaining)

    def test_delete_self_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        user = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.delete_user(user[0], user[0])
        self.assertIn("own account", str(ctx.exception))

    def test_delete_last_admin_fails(self):
        self.auth.create_user("onlyadmin", "pass", "admin")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='onlyadmin'")
        with self.assertRaises(Exception) as ctx:
            self.auth.delete_user(admin[0], 9999)
        self.assertIn("only admin", str(ctx.exception))

    def test_delete_user_with_tenant_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("tenantuser", "pass", "tenant")
        admin  = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        tenant = self.db.fetch_one("SELECT id FROM users WHERE username='tenantuser'")
        self.db.execute_query(
            "INSERT INTO tenants (user_id, ni_number, full_name, status) VALUES (?,?,?,?)",
            (tenant[0], "AB123456C", "Test Tenant", "Active"))
        with self.assertRaises(Exception) as ctx:
            self.auth.delete_user(tenant[0], admin[0])
        self.assertIn("tenant records", str(ctx.exception))

    def test_delete_nonexistent_user_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.delete_user(9999, admin[0])
        self.assertIn("not found", str(ctx.exception))

    # ── reset_password tests ──────────────────────────────────────────────────

    def test_reset_password_success(self):
        self.auth.create_user("admin1", "oldpass", "admin")
        user = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        self.auth.reset_password(user[0], "newpass123")
        self.assertIsNone(self.auth.login("admin1", "oldpass"))
        self.assertIsNotNone(self.auth.login("admin1", "newpass123"))

    def test_reset_password_too_short_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        user = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.reset_password(user[0], "abc")
        self.assertIn("6 characters", str(ctx.exception))

    def test_reset_password_empty_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        user = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.reset_password(user[0], "")
        self.assertIn("6 characters", str(ctx.exception))

    def test_reset_password_nonexistent_user_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.auth.reset_password(9999, "validpass")
        self.assertIn("not found", str(ctx.exception))

    # ── update_user tests ─────────────────────────────────────────────────────

    def test_update_user_role_and_dept(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("staff1", "pass", "maintenance", "EMP001", "Repairs")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        staff = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")
        self.auth.update_user(staff[0], "finance_manager", "EMP002", "Finance", admin[0])
        updated = self.db.fetch_one("SELECT role FROM users WHERE id=?", (staff[0],))
        self.assertEqual(updated[0], "finance_manager")
        s = self.db.fetch_one("SELECT employee_id, department FROM staff WHERE user_id=?", (staff[0],))
        self.assertEqual(s[0], "EMP002")
        self.assertEqual(s[1], "Finance")

    def test_update_user_self_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        user = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.update_user(user[0], "manager", "EMP001", "IT", user[0])
        self.assertIn("own account", str(ctx.exception))

    def test_update_demote_last_admin_fails(self):
        self.auth.create_user("onlyadmin", "pass", "admin")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='onlyadmin'")
        with self.assertRaises(Exception) as ctx:
            self.auth.update_user(admin[0], "manager", "EMP001", "IT", 9999)
        self.assertIn("only admin", str(ctx.exception))

    def test_update_admin_to_staff_creates_staff_record(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("admin2", "pass", "admin")
        a1 = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        a2 = self.db.fetch_one("SELECT id FROM users WHERE username='admin2'")
        self.auth.update_user(a2[0], "front_desk", "EMP010", "Reception", a1[0])
        staff = self.db.fetch_one("SELECT employee_id FROM staff WHERE user_id=?", (a2[0],))
        self.assertIsNotNone(staff)
        self.assertEqual(staff[0], "EMP010")

    def test_update_staff_to_admin_removes_staff_record(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("staff1", "pass", "manager", "EMP001", "Ops")
        a1    = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        staff = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")
        self.auth.update_user(staff[0], "admin", "", "", a1[0])
        s = self.db.fetch_one("SELECT user_id FROM staff WHERE user_id=?", (staff[0],))
        self.assertIsNone(s)

    def test_update_staff_role_no_employee_id_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        self.auth.create_user("staff1", "pass", "manager", "EMP001", "Ops")
        a1    = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        staff = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.update_user(staff[0], "maintenance", "", "", a1[0])
        self.assertIn("Employee ID is required", str(ctx.exception))

    def test_update_nonexistent_user_fails(self):
        self.auth.create_user("admin1", "pass", "admin")
        admin = self.db.fetch_one("SELECT id FROM users WHERE username='admin1'")
        with self.assertRaises(Exception) as ctx:
            self.auth.update_user(9999, "manager", "EMP001", "IT", admin[0])
        self.assertIn("not found", str(ctx.exception))
