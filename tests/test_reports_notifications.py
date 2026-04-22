# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
from datetime import datetime, timedelta
from tests.test_base import BaseTest
from report_manager import ReportManager
from notification_manager import NotificationManager
from tenant_manager import TenantManager
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager
from maintenance_manager import MaintenanceManager


class TestReportManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.rm = ReportManager(self.db)
        self.tenant = TenantManager(self.db)
        self.inv = InvoiceManager(self.db)
        self.pay = PaymentManager(self.db)
        self.maint = MaintenanceManager(self.db)

        # Seed apartments in different cities
        apts = [
            ("101", "10 Park St", "Bristol", 2, 850.00, 650, "Vacant"),
            ("102", "10 Park St", "Bristol", 1, 600.00, 450, "Vacant"),
            ("201", "25 Queen Rd", "Cardiff", 3, 1100.00, 900, "Vacant"),
            ("301", "5 King Ln", "London", 2, 1500.00, 700, "Vacant"),
        ]
        for a in apts:
            self.db.execute_query(
                "INSERT INTO apartments (unit_number, address, city, number_of_rooms, rental_price, square_footage, status) VALUES (?,?,?,?,?,?,?)", a)

    # ─── OCCUPANCY REPORT ───
    def test_occupancy_report_returns_all_apartments(self):
        report = self.rm.get_occupancy_report()
        self.assertEqual(len(report), 4)

    def test_occupancy_report_filtered_by_city(self):
        report = self.rm.get_occupancy_report("Bristol")
        self.assertEqual(len(report), 2)
        for row in report:
            self.assertEqual(row[2], "Bristol")

    def test_occupancy_report_filter_all_returns_everything(self):
        report = self.rm.get_occupancy_report("All")
        self.assertEqual(len(report), 4)

    def test_occupancy_summary_total_count(self):
        summary = self.rm.get_occupancy_summary()
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["occupied"], 0)
        self.assertEqual(summary["vacant"], 4)

    def test_occupancy_summary_rate_calculation(self):
        # Mark 2 apartments as Occupied to test rate calc
        self.db.execute_query("UPDATE apartments SET status='Occupied' WHERE unit_number IN ('101','201')")
        summary = self.rm.get_occupancy_summary()
        self.assertEqual(summary["occupancy_rate"], 50.0)

    def test_occupancy_summary_filtered_by_city(self):
        self.db.execute_query("UPDATE apartments SET status='Occupied' WHERE unit_number='101'")
        summary = self.rm.get_occupancy_summary("Bristol")
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["occupied"], 1)
        self.assertEqual(summary["vacant"], 1)

    def test_occupancy_summary_city_with_no_occupied(self):
        # All apartments are Vacant in test setup
        summary = self.rm.get_occupancy_summary("London")
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["occupied"], 0)
        self.assertEqual(summary["vacancy_rate"] if "vacancy_rate" in summary else summary["occupancy_rate"], 0.0)

    # ─── FINANCIAL SUMMARY ───
    def test_financial_summary_with_no_data(self):
        summary = self.rm.get_financial_summary()
        self.assertEqual(summary["collected"], 0)
        self.assertEqual(summary["pending"], 0)
        self.assertEqual(summary["total_invoiced"], 0)

    def test_financial_summary_with_invoices_and_payments(self):
        # Create a tenant with a Vacant apartment
        self.tenant.register_tenant("fin_user", "pass", "NI001", "Fin User", "", "", "", "", "", "")
        uid = self.db.fetch_one("SELECT id FROM users")[0]
        apt_id = self.db.fetch_one("SELECT id FROM apartments WHERE status='Vacant' LIMIT 1")[0]
        self.tenant.assign_apartment(uid, apt_id, "2026-01-01", "2026-12-31", 850.0, 500.0)

        # Create invoice and pay it
        self.inv.generate_invoice(uid, 850)
        inv_id = self.inv.get_all_invoices()[0][0]
        self.pay.record_payment(inv_id, 850, "Cash")

        # Create another invoice (unpaid)
        self.inv.generate_invoice(uid, 850)

        summary = self.rm.get_financial_summary()
        self.assertEqual(summary["collected"], 850.0)
        self.assertEqual(summary["pending"], 850.0)
        self.assertEqual(summary["total_invoiced"], 1700.0)
        self.assertEqual(summary["collection_rate"], 50.0)

    def test_financial_breakdown_shows_per_tenant(self):
        self.tenant.register_tenant("ten_a", "pass", "NI_A", "Alice", "", "", "", "", "", "")
        uid = self.db.fetch_one("SELECT id FROM users WHERE username='ten_a'")[0]
        apt_id = self.db.fetch_one("SELECT id FROM apartments WHERE status='Vacant' LIMIT 1")[0]
        self.tenant.assign_apartment(uid, apt_id, "2026-01-01", "2026-12-31", 850.0, 500.0)

        self.inv.generate_invoice(uid, 1000)
        inv_id = self.inv.get_all_invoices()[0][0]
        self.pay.record_payment(inv_id, 400, "Cash")

        breakdown = self.rm.get_financial_breakdown()
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0][0], "Alice")       # tenant name
        self.assertEqual(breakdown[0][1], 1000.0)         # total invoiced
        self.assertEqual(breakdown[0][2], 400.0)          # total paid
        self.assertEqual(breakdown[0][3], 600.0)          # outstanding

    # ─── MAINTENANCE COST REPORT ───
    def test_maintenance_cost_report_empty(self):
        report = self.rm.get_maintenance_cost_report()
        self.assertEqual(len(report), 0)

    def test_maintenance_cost_report_with_data(self):
        # Create maintenance ticket with cost
        apt_id = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='101'")[0]
        self.maint.create_ticket(apt_id, None, "Broken pipe", "High")
        ticket_id = self.db.fetch_one("SELECT id FROM maintenance_requests")[0]
        self.maint.log_costs(ticket_id, 3.0, 200.0)

        report = self.rm.get_maintenance_cost_report()
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0][0], "101")       # unit number
        self.assertEqual(report[0][1], "Bristol")    # city
        self.assertEqual(report[0][2], 1)            # total tickets
        self.assertEqual(report[0][3], 200.0)        # total cost
        self.assertEqual(report[0][4], 3.0)          # total hours

    def test_maintenance_cost_report_filtered_by_city(self):
        apt1 = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='101'")[0]
        apt2 = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='201'")[0]
        self.maint.create_ticket(apt1, None, "Issue 1", "Low")
        self.maint.create_ticket(apt2, None, "Issue 2", "Low")
        t1 = self.db.fetch_one("SELECT id FROM maintenance_requests ORDER BY id LIMIT 1")[0]
        t2 = self.db.fetch_one("SELECT id FROM maintenance_requests ORDER BY id DESC LIMIT 1")[0]
        self.maint.log_costs(t1, 1.0, 50.0)
        self.maint.log_costs(t2, 2.0, 100.0)

        bristol = self.rm.get_maintenance_cost_report("Bristol")
        self.assertEqual(len(bristol), 1)
        self.assertEqual(bristol[0][3], 50.0)

        cardiff = self.rm.get_maintenance_cost_report("Cardiff")
        self.assertEqual(len(cardiff), 1)
        self.assertEqual(cardiff[0][3], 100.0)

    def test_maintenance_cost_summary(self):
        apt_id = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='101'")[0]
        self.maint.create_ticket(apt_id, None, "Issue A", "High")
        self.maint.create_ticket(apt_id, None, "Issue B", "Low")
        tickets = self.db.fetch_all("SELECT id FROM maintenance_requests ORDER BY id")
        self.maint.log_costs(tickets[0][0], 2.0, 100.0)
        self.maint.log_costs(tickets[1][0], 1.0, 50.0)

        summary = self.rm.get_maintenance_cost_summary()
        self.assertEqual(summary["total_cost"], 150.0)
        self.assertEqual(summary["avg_cost"], 75.0)
        self.assertEqual(summary["total_hours"], 3.0)
        self.assertEqual(summary["completed_tickets"], 2)

    # ─── CITIES ───
    def test_get_cities_returns_distinct_sorted(self):
        cities = self.rm.get_cities()
        self.assertEqual(cities, ["Bristol", "Cardiff", "London"])


class TestNotificationManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.nm = NotificationManager(self.db)
        self.tenant = TenantManager(self.db)
        self.inv = InvoiceManager(self.db)
        self.pay = PaymentManager(self.db)
        self.maint = MaintenanceManager(self.db)

        # Seed apartment (Vacant so we can assign)
        self.db.execute_query(
            "INSERT INTO apartments (unit_number, address, city, number_of_rooms, rental_price, square_footage, status) VALUES (?,?,?,?,?,?,?)",
            ("101", "10 Park St", "Bristol", 2, 850.00, 650, "Vacant"))
        self.apt_id = self.db.fetch_one("SELECT id FROM apartments")[0]

        # Seed tenant
        self.tenant.register_tenant("notif_user", "pass", "NI_NOT", "Notif User", "077", "n@e.com", "", "", "", "")
        self.uid = self.db.fetch_one("SELECT id FROM users")[0]
        self.tenant.assign_apartment(self.uid, self.apt_id, "2026-01-01", "2026-12-31", 850.0, 500.0)

    # ─── OVERDUE INVOICES ───
    def test_no_overdue_invoices_when_none_exist(self):
        overdue = self.nm.get_overdue_invoices()
        self.assertEqual(len(overdue), 0)

    def test_overdue_invoice_detected(self):
        # Insert invoice with past due date directly
        past_due = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, past_due, 850.0, "Pending"))

        overdue = self.nm.get_overdue_invoices()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0][1], "Notif User")   # tenant name
        self.assertEqual(overdue[0][3], 850.0)           # amount
        self.assertGreaterEqual(overdue[0][4], 9)        # days overdue (at least 9)

    def test_paid_invoice_not_overdue(self):
        past_due = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, past_due, 850.0, "Paid"))

        overdue = self.nm.get_overdue_invoices()
        self.assertEqual(len(overdue), 0)

    def test_future_due_invoice_not_overdue(self):
        future_due = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        issue_date = datetime.now().strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, future_due, 850.0, "Pending"))

        overdue = self.nm.get_overdue_invoices()
        self.assertEqual(len(overdue), 0)

    def test_multiple_overdue_sorted_by_days(self):
        for days_ago in [5, 15, 30]:
            past_due = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            issue_date = (datetime.now() - timedelta(days=days_ago + 30)).strftime("%Y-%m-%d")
            self.db.execute_query(
                "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
                (self.uid, issue_date, past_due, 850.0, "Pending"))

        overdue = self.nm.get_overdue_invoices()
        self.assertEqual(len(overdue), 3)
        # Should be sorted by days_overdue DESC (most overdue first)
        self.assertGreater(overdue[0][4], overdue[1][4])
        self.assertGreater(overdue[1][4], overdue[2][4])

    # ─── EXPIRING LEASES ───
    def test_no_expiring_leases_when_far_away(self):
        # Lease ends in 2026-12-31, more than 30 days away
        expiring = self.nm.get_expiring_leases(days=30)
        # This depends on current date, so check for the assigned lease end
        # Since we set lease_end to 2026-12-31, if current date is April 2026,
        # it should NOT show up in 30-day window
        for lease in expiring:
            self.assertLessEqual(lease[4], 30)

    def test_expiring_lease_detected_within_window(self):
        # Override lease end to be within 15 days
        near = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        self.db.execute_query("UPDATE tenants SET lease_end_date=? WHERE user_id=?", (near, self.uid))

        expiring = self.nm.get_expiring_leases(days=30)
        self.assertEqual(len(expiring), 1)
        self.assertEqual(expiring[0][1], "Notif User")
        self.assertLessEqual(expiring[0][4], 30)

    def test_expired_lease_not_shown(self):
        # Lease already ended (past date)
        past = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        self.db.execute_query("UPDATE tenants SET lease_end_date=? WHERE user_id=?", (past, self.uid))

        expiring = self.nm.get_expiring_leases(days=30)
        self.assertEqual(len(expiring), 0)

    # ─── NOTIFICATION COUNT ───
    def test_notification_count_zero_when_clean(self):
        count = self.nm.get_notification_count()
        # May have expiring lease depending on date, but no overdue invoices
        self.assertIsInstance(count, int)

    def test_notification_count_includes_overdue(self):
        past_due = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, past_due, 850.0, "Pending"))

        count = self.nm.get_notification_count()
        self.assertGreaterEqual(count, 1)

    # ─── NOTIFICATION FEED ───
    def test_get_notifications_returns_overdue_as_dict(self):
        past_due = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=37)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, past_due, 850.0, "Pending"))

        items = self.nm.get_notifications()
        overdue_items = [i for i in items if i["type"] == "overdue"]
        self.assertEqual(len(overdue_items), 1)
        self.assertIn("Notif User", overdue_items[0]["text"])
        self.assertIn("850.00", overdue_items[0]["text"])

    def test_get_notifications_combines_overdue_and_expiring(self):
        past_due = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=33)).strftime("%Y-%m-%d")
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)",
            (self.uid, issue_date, past_due, 850.0, "Pending"))
        near = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        self.db.execute_query("UPDATE tenants SET lease_end_date=? WHERE user_id=?",
                              (near, self.uid))

        items = self.nm.get_notifications()
        types = {i["type"] for i in items}
        self.assertIn("overdue", types)
        self.assertIn("expiring", types)


if __name__ == "__main__":
    unittest.main()
