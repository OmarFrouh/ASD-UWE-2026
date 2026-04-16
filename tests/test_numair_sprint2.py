# Student Name: Numair
# Student ID: 24026758

"""
Comprehensive tests for Numair's Sprint 2 work.
Tests cover:
  - MaintenanceManager: get_cost_report_by_apartment()
  - MaintenanceManager: get_cost_report_by_city()
  - MaintenanceManager: get_tickets_by_status_count()
  - MaintenanceManager: notify_tenant_scheduled_date()
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tests.test_base import BaseTest
from maintenance_manager import MaintenanceManager
from property_manager import PropertyManager


class NumairTestBase(BaseTest):
    """Shared setup for Numair's Sprint 2 test classes."""

    def setUp(self):
        super().setUp()
        self.maint = MaintenanceManager(self.db)
        self.prop = PropertyManager(self.db)

        # Two apartments in different cities
        self.prop.add_apartment("A101", "1 High St", 800.00, 50.0, city="Bristol")
        self.prop.add_apartment("B201", "2 Low St",  700.00, 45.0, city="Cardiff")

        apts = self.prop.get_all_apartments()
        self.apt_bristol = apts[0][0]   # id of A101
        self.apt_cardiff = apts[1][0]   # id of B201

        # A tenant linked to the Bristol apartment
        self.db.execute_query(
            "INSERT INTO users (id, username, password_hash, role) "
            "VALUES (200, 'testtenant2', 'hash', 'tenant')"
        )
        self.db.execute_query(
            """INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email,
               occupation, apartment_id, monthly_rent, status, lease_start_date, lease_end_date)
               VALUES (200, 'ZZ999999Z', 'Jane Smith', '07700000002', 'jane@test.com',
                       'Nurse', ?, 800.00, 'Active', '2026-01-01', '2027-01-01')""",
            (self.apt_bristol,)
        )
        self.tenant_id = 200

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _ticket(self, apt_id, tenant_id=None, desc="Issue", priority="Medium"):
        self.maint.create_ticket(apt_id, tenant_id, desc, priority)
        return self.db.fetch_one(
            "SELECT id FROM maintenance_requests ORDER BY id DESC LIMIT 1")[0]

    def _set_cost(self, ticket_id, cost, hours=1.0):
        self.maint.log_costs(ticket_id, hours, cost)

    def _set_status(self, ticket_id, status):
        # Drive through valid transitions to reach target
        path_to = {
            "Open":       [],
            "Assigned":   ["Assigned"],
            "In Progress":["In Progress"],
            "Fixed":      ["In Progress", "Fixed"],
            "Closed":     ["In Progress", "Fixed", "Closed"],
        }
        for s in path_to[status]:
            self.db.execute_query(
                "UPDATE maintenance_requests SET status=? WHERE id=?", (s, ticket_id))


# ════════════════════════════════════════════════════════════════════════════
# MaintenanceManager — get_cost_report_by_apartment
# ════════════════════════════════════════════════════════════════════════════
class TestCostReportByApartment(NumairTestBase):

    def test_returns_list(self):
        self._ticket(self.apt_bristol)
        self.assertIsInstance(self.maint.get_cost_report_by_apartment(), list)

    def test_empty_when_no_tickets(self):
        """No maintenance requests → no rows (apartments with no tickets excluded)."""
        self.assertEqual(self.maint.get_cost_report_by_apartment(), [])

    def test_row_has_8_fields(self):
        """Each row: (unit, city, total, open, resolved, cost, hours, avg)."""
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(len(row), 8)

    def test_correct_unit_and_city(self):
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(row[0], "A101")
        self.assertEqual(row[1], "Bristol")

    def test_total_ticket_count(self):
        self._ticket(self.apt_bristol)
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(row[2], 2)  # total_tickets

    def test_open_tickets_count(self):
        """Open, Assigned, In Progress all count as open."""
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(self.apt_bristol)
        t3 = self._ticket(self.apt_bristol)
        self._set_status(t2, "Assigned")
        self._set_status(t3, "In Progress")
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(row[3], 3)  # all 3 are "open" statuses

    def test_resolved_tickets_count(self):
        """Fixed and Closed count as resolved."""
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(self.apt_bristol)
        self._set_status(t1, "Fixed")
        self._set_status(t2, "Closed")
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(row[4], 2)  # resolved

    def test_total_cost_correct(self):
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(self.apt_bristol)
        self._set_cost(t1, 100.0)
        self._set_cost(t2, 50.0)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertAlmostEqual(row[5], 150.0)  # total_cost

    def test_total_hours_correct(self):
        t1 = self._ticket(self.apt_bristol)
        self._set_cost(t1, 100.0, hours=3.5)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertAlmostEqual(row[6], 3.5)  # total_hours

    def test_zero_cost_when_no_logging(self):
        """Tickets with no cost logged should show 0, not NULL."""
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_apartment()[0]
        self.assertEqual(row[5], 0)   # total_cost
        self.assertEqual(row[6], 0)   # total_hours

    def test_sorted_by_cost_desc(self):
        """Apartment with higher cost should appear first."""
        t_bristol = self._ticket(self.apt_bristol)
        t_cardiff = self._ticket(self.apt_cardiff)
        self._set_cost(t_bristol, 50.0)
        self._set_cost(t_cardiff, 200.0)
        rows = self.maint.get_cost_report_by_apartment()
        self.assertGreaterEqual(rows[0][5], rows[1][5])

    def test_two_apartments_both_returned(self):
        self._ticket(self.apt_bristol)
        self._ticket(self.apt_cardiff)
        self.assertEqual(len(self.maint.get_cost_report_by_apartment()), 2)

    def test_apartment_without_tickets_excluded(self):
        """An apartment with no tickets must not appear in the report."""
        self._ticket(self.apt_bristol)  # only Bristol has a ticket
        rows = self.maint.get_cost_report_by_apartment()
        units = [r[0] for r in rows]
        self.assertIn("A101", units)
        self.assertNotIn("B201", units)


# ════════════════════════════════════════════════════════════════════════════
# MaintenanceManager — get_cost_report_by_city
# ════════════════════════════════════════════════════════════════════════════
class TestCostReportByCity(NumairTestBase):

    def test_returns_list(self):
        self._ticket(self.apt_bristol)
        self.assertIsInstance(self.maint.get_cost_report_by_city(), list)

    def test_empty_when_no_tickets(self):
        self.assertEqual(self.maint.get_cost_report_by_city(), [])

    def test_row_has_5_fields(self):
        """Each row: (city, total_tickets, total_cost, total_hours, avg_cost)."""
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_city()[0]
        self.assertEqual(len(row), 5)

    def test_correct_city_name(self):
        self._ticket(self.apt_bristol)
        row = self.maint.get_cost_report_by_city()[0]
        self.assertEqual(row[0], "Bristol")

    def test_total_cost_per_city(self):
        t = self._ticket(self.apt_bristol)
        self._set_cost(t, 120.0)
        row = next(r for r in self.maint.get_cost_report_by_city() if r[0] == "Bristol")
        self.assertAlmostEqual(row[2], 120.0)

    def test_multiple_apartments_same_city_grouped(self):
        """Two apartments in Bristol → their tickets merge into one Bristol row."""
        self.prop.add_apartment("A102", "3 High St", 850.00, 55.0, city="Bristol")
        apt2 = self.prop.get_all_apartments()[2][0]
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(apt2)
        self._set_cost(t1, 100.0)
        self._set_cost(t2, 80.0)
        row = next(r for r in self.maint.get_cost_report_by_city() if r[0] == "Bristol")
        self.assertEqual(row[1], 2)            # 2 tickets
        self.assertAlmostEqual(row[2], 180.0)  # combined cost

    def test_two_cities_both_returned(self):
        self._ticket(self.apt_bristol)
        self._ticket(self.apt_cardiff)
        cities = [r[0] for r in self.maint.get_cost_report_by_city()]
        self.assertIn("Bristol", cities)
        self.assertIn("Cardiff", cities)

    def test_sorted_by_cost_desc(self):
        t_b = self._ticket(self.apt_bristol)
        t_c = self._ticket(self.apt_cardiff)
        self._set_cost(t_b, 50.0)
        self._set_cost(t_c, 300.0)
        rows = self.maint.get_cost_report_by_city()
        self.assertGreaterEqual(rows[0][2], rows[1][2])

    def test_zero_cost_when_no_logging(self):
        self._ticket(self.apt_bristol)
        row = next(r for r in self.maint.get_cost_report_by_city() if r[0] == "Bristol")
        self.assertEqual(row[2], 0)


# ════════════════════════════════════════════════════════════════════════════
# MaintenanceManager — get_tickets_by_status_count
# ════════════════════════════════════════════════════════════════════════════
class TestTicketsByStatusCount(NumairTestBase):

    def test_returns_dict(self):
        self.assertIsInstance(self.maint.get_tickets_by_status_count(), dict)

    def test_empty_when_no_tickets(self):
        self.assertEqual(self.maint.get_tickets_by_status_count(), {})

    def test_single_open_ticket(self):
        self._ticket(self.apt_bristol)
        result = self.maint.get_tickets_by_status_count()
        self.assertIn("Open", result)
        self.assertEqual(result["Open"], 1)

    def test_multiple_statuses(self):
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(self.apt_bristol)
        t3 = self._ticket(self.apt_bristol)
        self._set_status(t2, "In Progress")
        self._set_status(t3, "Fixed")
        result = self.maint.get_tickets_by_status_count()
        self.assertEqual(result["Open"], 1)
        self.assertEqual(result["In Progress"], 1)
        self.assertEqual(result["Fixed"], 1)

    def test_count_correct_with_many_open(self):
        for _ in range(4):
            self._ticket(self.apt_bristol)
        result = self.maint.get_tickets_by_status_count()
        self.assertEqual(result["Open"], 4)

    def test_sum_equals_total_tickets(self):
        t1 = self._ticket(self.apt_bristol)
        t2 = self._ticket(self.apt_bristol)
        t3 = self._ticket(self.apt_cardiff)
        self._set_status(t2, "Fixed")
        result = self.maint.get_tickets_by_status_count()
        self.assertEqual(sum(result.values()), 3)

    def test_only_present_statuses_in_dict(self):
        """Dict must only contain statuses that actually have tickets."""
        self._ticket(self.apt_bristol)
        result = self.maint.get_tickets_by_status_count()
        self.assertNotIn("Fixed", result)
        self.assertNotIn("Closed", result)


# ════════════════════════════════════════════════════════════════════════════
# MaintenanceManager — notify_tenant_scheduled_date
# ════════════════════════════════════════════════════════════════════════════
class TestNotifyTenantScheduledDate(NumairTestBase):

    def setUp(self):
        super().setUp()
        # Ticket linked to our tenant
        self.ticket_with_tenant = self._ticket(
            self.apt_bristol, tenant_id=self.tenant_id, desc="Boiler issue")
        # Ticket with no tenant linked
        self.ticket_no_tenant = self._ticket(
            self.apt_cardiff, tenant_id=None, desc="Window crack")

    def test_raises_on_invalid_ticket_id(self):
        with self.assertRaises(Exception) as ctx:
            self.maint.notify_tenant_scheduled_date(9999, "2026-04-15")
        self.assertIn("Ticket not found", str(ctx.exception))

    def test_returns_dict(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        self.assertIsInstance(result, dict)

    def test_scheduled_date_stored_in_db(self):
        self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        row = self.db.fetch_one(
            "SELECT scheduled_date FROM maintenance_requests WHERE id=?",
            (self.ticket_with_tenant,))
        self.assertEqual(row[0], "2026-04-15")

    def test_correct_date_returned_in_dict(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-20")
        self.assertEqual(result["scheduled_date"], "2026-04-20")

    def test_correct_ticket_id_returned(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        self.assertEqual(result["ticket_id"], self.ticket_with_tenant)

    def test_tenant_name_returned(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        self.assertEqual(result["tenant_name"], "Jane Smith")

    def test_tenant_phone_returned(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        self.assertEqual(result["phone"], "07700000002")

    def test_tenant_email_returned(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-15")
        self.assertEqual(result["email"], "jane@test.com")

    def test_no_tenant_linked_returns_fallback(self):
        result = self.maint.notify_tenant_scheduled_date(self.ticket_no_tenant, "2026-04-15")
        self.assertEqual(result["tenant_name"], "No tenant linked")

    def test_no_tenant_linked_still_stores_date(self):
        """Date must be saved even when there is no tenant linked to the ticket."""
        self.maint.notify_tenant_scheduled_date(self.ticket_no_tenant, "2026-05-01")
        row = self.db.fetch_one(
            "SELECT scheduled_date FROM maintenance_requests WHERE id=?",
            (self.ticket_no_tenant,))
        self.assertEqual(row[0], "2026-05-01")

    def test_can_update_date_twice(self):
        """Calling notify again on the same ticket should overwrite the date."""
        self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-10")
        self.maint.notify_tenant_scheduled_date(self.ticket_with_tenant, "2026-04-20")
        row = self.db.fetch_one(
            "SELECT scheduled_date FROM maintenance_requests WHERE id=?",
            (self.ticket_with_tenant,))
        self.assertEqual(row[0], "2026-04-20")


if __name__ == "__main__":
    unittest.main(verbosity=2)
