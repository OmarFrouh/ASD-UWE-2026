import unittest
from tests.test_base import BaseTest
from maintenance_manager import MaintenanceManager
from property_manager import PropertyManager

class TestMaintenanceManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.maint = MaintenanceManager(self.db)
        self.prop = PropertyManager(self.db)
        
        self.prop.add_apartment("M100", "Maintenance Way", 1000, 500)
        self.apt_id = self.prop.get_all_apartments()[0][0]

    def test_create_ticket(self):
        self.maint.create_ticket(self.apt_id, None, "Leaky faucet", "High")
        tickets = self.maint.get_all_tickets()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0][3], "Leaky faucet")
        self.assertEqual(tickets[0][5], "Open")

    def test_invalid_ticket_creation(self):
        # Invalid priority
        with self.assertRaises(Exception) as ctx:
            self.maint.create_ticket(self.apt_id, None, "Broken window", "Super Urgent")
        self.assertIn("Priority must be", str(ctx.exception))
        
        # Invalid apartment
        with self.assertRaises(Exception) as ctx:
            self.maint.create_ticket(999, None, "Broken window", "Urgent")
        self.assertIn("Apartment not found", str(ctx.exception))

    def test_log_costs_accumulates_correctly(self):
        # We explicitly fixed this logic bug earlier, testing to ensure it works
        self.maint.create_ticket(self.apt_id, None, "Wall repair", "Low")
        ticket_id = self.maint.get_all_tickets()[0][0]
        
        self.maint.log_costs(ticket_id, 2.5, 100)
        
        t = self.db.fetch_one("SELECT time_spent, cost FROM maintenance_requests WHERE id=?", (ticket_id,))
        self.assertEqual(t[0], 2.5)
        self.assertEqual(t[1], 100.0)
        
        # Log more costs
        self.maint.log_costs(ticket_id, 1.0, 50)
        
        t = self.db.fetch_one("SELECT time_spent, cost FROM maintenance_requests WHERE id=?", (ticket_id,))
        self.assertEqual(t[0], 3.5)
        self.assertEqual(t[1], 150.0)

    def test_log_negative_costs_blocked(self):
        self.maint.create_ticket(self.apt_id, None, "Heater", "High")
        ticket_id = self.maint.get_all_tickets()[0][0]
        
        with self.assertRaises(Exception) as ctx:
            self.maint.log_costs(ticket_id, -1, -50)
        self.assertIn("Time and cost must be positive", str(ctx.exception))
