# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
import sys
import os

# Ensure the root project path is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database_manager import DatabaseManager

class BaseTest(unittest.TestCase):
    def setUp(self):
        """Runs before every test. Creates a fresh, transient database."""
        self.db_path = "tests/test_temp.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.db = DatabaseManager(self.db_path)
        # Suppress prints from setup
        old_stdout = sys.stdout
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        self.db.create_tables()
        sys.stdout = old_stdout
        devnull.close()

    def tearDown(self):
        """Runs after every test to clean up."""
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass
