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
