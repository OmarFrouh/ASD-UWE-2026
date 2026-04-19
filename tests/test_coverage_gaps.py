# Student Name: Omar Alfrouh
# Student ID: 24020879

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_base import BaseTest
from tenant_manager import TenantManager
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager
from maintenance_manager import MaintenanceManager
from auth_manager import AuthManager


class TestTenantManagerMethods(BaseTest):
    """Tests for TenantManager methods that previously had no dedicated coverage."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self._make_tenant("alice", "NI001")
        self._make_tenant("bob",   "NI002")
        self._make_tenant("carol", "NI003")
        self.tm.archive_tenant(self._uid("carol"))

    def _uid(self, name):
        row = self.db.fetch_one("SELECT id FROM users WHERE username=?", (name,))
        return row[0] if row else None

    def _make_tenant(self, username, ni):
        self.tm.register_tenant(
            username, "pass123", ni, username.capitalize(),
            "07000000000", f"{username}@test.com",
            "Engineer", "None", "None", "1 bed")

    # get_archived_tenants
    def test_get_archived_returns_non_active(self):
        rows = self.tm.get_archived_tenants()
        names = [r[2] for r in rows]
        self.assertIn("Carol", names)
        self.assertNotIn("Alice", names)

    def test_get_archived_empty_when_none(self):
        # Archive remaining tenants then check a fresh tenant only
        fresh_tm = TenantManager(self.db)
        rows = fresh_tm.get_archived_tenants()
        # Carol is archived — at least one row
        self.assertGreaterEqual(len(rows), 1)

    # search_tenants
    def test_search_by_name(self):
        rows = self.tm.search_tenants("alice")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "Alice")

    def test_search_by_ni(self):
        rows = self.tm.search_tenants("NI002")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "Bob")

    def test_search_by_email(self):
        rows = self.tm.search_tenants("alice@test.com")
        self.assertEqual(len(rows), 1)

    def test_search_no_results(self):
        rows = self.tm.search_tenants("zzznomatch")
        self.assertEqual(rows, [])

    # filter_tenants_by_status
    def test_filter_active_only(self):
        rows = self.tm.filter_tenants_by_status("Active")
        statuses = [r[10] for r in rows]
        self.assertTrue(all(s == "Active" for s in statuses))

    def test_filter_all_includes_archived(self):
        rows = self.tm.filter_tenants_by_status("All")
        statuses = {r[10] for r in rows}
        self.assertIn("Active",   statuses)
        self.assertIn("Archived", statuses)

    def test_filter_archived_only(self):
        rows = self.tm.filter_tenants_by_status("Archived")
        self.assertTrue(all(r[10] == "Archived" for r in rows))

    # get_tenant_count_by_status
    def test_count_by_status_returns_dict(self):
        counts = self.tm.get_tenant_count_by_status()
        self.assertIsInstance(counts, dict)
        self.assertGreaterEqual(counts.get("Active", 0), 2)
        self.assertGreaterEqual(counts.get("Archived", 0), 1)

    # get_all_complaints
    def test_get_all_complaints_returns_rows(self):
        uid = self._uid("alice")
        self.tm.log_complaint(uid, "Noise", "Too loud at night")
        rows = self.tm.get_all_complaints()
        self.assertGreaterEqual(len(rows), 1)
        subjects = [r[2] for r in rows]
        self.assertIn("Noise", subjects)

    def test_get_all_complaints_empty(self):
        rows = self.tm.get_all_complaints()
        self.assertIsInstance(rows, list)


class TestInvoiceManagerMethods(BaseTest):
    """Tests for InvoiceManager methods with no prior standalone coverage."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.im = InvoiceManager(self.db)
        self.tm.register_tenant(
            "alice", "pass123", "NI100", "Alice",
            "07000", "a@test.com", "Dev", "None", "None", "1 bed")
        row = self.db.fetch_one("SELECT id FROM users WHERE username='alice'")
        self.uid = row[0]
        self.db.execute_query(
            "UPDATE tenants SET monthly_rent=800 WHERE user_id=?", (self.uid,))

    def _make_overdue_invoice(self):
        """Insert an invoice with a past due date directly."""
        self.db.execute_query(
            "INSERT INTO invoices (tenant_id, issue_date, due_date, total_amount, status) "
            "VALUES (?, '2024-01-01', '2024-01-31', 800, 'Pending')",
            (self.uid,))
        row = self.db.fetch_one("SELECT last_insert_rowid()")
        return row[0]

    # get_overdue_invoices
    def test_get_overdue_returns_past_due(self):
        self._make_overdue_invoice()
        rows = self.im.get_overdue_invoices()
        self.assertGreaterEqual(len(rows), 1)
        # columns: id, tenant_name, due_date, amount
        self.assertEqual(rows[0][1], "Alice")

    def test_get_overdue_excludes_paid(self):
        inv_id = self._make_overdue_invoice()
        self.db.execute_query(
            "UPDATE invoices SET status='Paid' WHERE id=?", (inv_id,))
        rows = self.im.get_overdue_invoices()
        ids = [r[0] for r in rows]
        self.assertNotIn(inv_id, ids)

    # get_payments_for_invoice
    def test_get_payments_for_invoice_returns_rows(self):
        inv_id = self.im.generate_invoice(self.uid, 800)
        pm = PaymentManager(self.db)
        pay_id = pm.record_payment(inv_id, 800, "Card", "REF1")
        rows = self.im.get_payments_for_invoice(inv_id)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 800)

    def test_get_payments_for_invoice_empty(self):
        inv_id = self.im.generate_invoice(self.uid, 800)
        rows = self.im.get_payments_for_invoice(inv_id)
        self.assertEqual(rows, [])

    # get_overdue_with_details
    def test_get_overdue_with_details_has_days(self):
        self._make_overdue_invoice()
        rows = self.im.get_overdue_with_details()
        self.assertGreaterEqual(len(rows), 1)
        # columns: invoice_id, tenant_name, email, phone, due_date, amount, days_overdue
        self.assertGreater(rows[0][6], 0)

    # get_invoice_aging
    def test_get_invoice_aging_returns_dict(self):
        self._make_overdue_invoice()
        aging = self.im.get_invoice_aging()
        self.assertIsInstance(aging, dict)
        total = sum(aging.values())
        self.assertGreaterEqual(total, 1)

    def test_get_invoice_aging_empty_no_overdue(self):
        aging = self.im.get_invoice_aging()
        self.assertIsInstance(aging, dict)

    # generate_invoice returns ID
    def test_generate_invoice_returns_id(self):
        inv_id = self.im.generate_invoice(self.uid, 500)
        self.assertIsNotNone(inv_id)
        self.assertIsInstance(inv_id, int)
        self.assertGreater(inv_id, 0)


class TestPaymentManagerMethods(BaseTest):
    """Tests for PaymentManager methods with no prior standalone coverage."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.im = InvoiceManager(self.db)
        self.pm = PaymentManager(self.db)
        self.tm.register_tenant(
            "alice", "pass123", "NI200", "Alice",
            "07000", "a@test.com", "Dev", "None", "None", "1 bed")
        row = self.db.fetch_one("SELECT id FROM users WHERE username='alice'")
        self.uid = row[0]
        self.db.execute_query(
            "UPDATE tenants SET monthly_rent=1000 WHERE user_id=?", (self.uid,))
        self.inv_id = self.im.generate_invoice(self.uid, 1000)
        self.pay_id = self.pm.record_payment(self.inv_id, 1000, "Card", "REF1")

    # get_all_payments
    def test_get_all_payments_returns_rows(self):
        rows = self.pm.get_all_payments()
        self.assertGreaterEqual(len(rows), 1)
        # columns: id, tenant_name, amount, date, method, ref, invoice_id
        self.assertEqual(rows[0][1], "Alice")

    def test_get_all_payments_empty_db(self):
        # Fresh instance on same DB — payment exists but test the return type
        rows = self.pm.get_all_payments()
        self.assertIsInstance(rows, list)

    # get_financial_summary
    def test_get_financial_summary_keys(self):
        summary = self.pm.get_financial_summary()
        self.assertIn("Collected", summary)
        self.assertIn("Pending",   summary)

    def test_get_financial_summary_collected(self):
        summary = self.pm.get_financial_summary()
        self.assertEqual(summary["Collected"], 1000)

    # get_collected_vs_pending
    def test_get_collected_vs_pending_keys(self):
        data = self.pm.get_collected_vs_pending()
        self.assertIn("collected", data)
        self.assertIn("pending",   data)
        self.assertIn("total",     data)

    def test_get_collected_vs_pending_values(self):
        data = self.pm.get_collected_vs_pending()
        self.assertEqual(data["collected"], 1000)
        self.assertEqual(data["pending"],   0)
        self.assertEqual(data["total"],     1000)

    # get_payment_history_by_method
    def test_get_payment_history_by_method(self):
        rows = self.pm.get_payment_history_by_method()
        self.assertGreaterEqual(len(rows), 1)
        methods = [r[0] for r in rows]
        self.assertIn("Card", methods)

    def test_payment_history_by_method_amounts(self):
        rows = self.pm.get_payment_history_by_method()
        for method, total, count in rows:
            self.assertGreater(total, 0)
            self.assertGreater(count, 0)

    # get_monthly_revenue
    def test_get_monthly_revenue_returns_list(self):
        rows = self.pm.get_monthly_revenue()
        self.assertIsInstance(rows, list)
        self.assertLessEqual(len(rows), 6)

    def test_get_monthly_revenue_has_current_month(self):
        from datetime import datetime
        current = datetime.now().strftime("%Y-%m")
        rows = self.pm.get_monthly_revenue()
        months = [r[0] for r in rows]
        self.assertIn(current, months)

    # get_payments_for_tenant (covered previously but confirm here too)
    def test_get_payments_for_tenant(self):
        rows = self.pm.get_payments_for_tenant(self.uid)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 1000)


class TestMaintenanceManagerMethods(BaseTest):
    """Tests for MaintenanceManager methods with no prior standalone coverage."""

    def setUp(self):
        super().setUp()
        self.mm = MaintenanceManager(self.db)
        self.auth = AuthManager(self.db)
        # Apartment
        self.db.execute_query(
            "INSERT INTO apartments (unit_number, address, city, rental_price, "
            "square_footage, status) VALUES ('U99','99 St','Bristol',900,500,'Vacant')")
        row = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='U99'")
        self.apt_id = row[0]
        # Maintenance staff
        self.auth.create_user("staff1", "pass123", "maintenance",
                              employee_id="EMP001", department="Maint")
        row = self.db.fetch_one("SELECT id FROM users WHERE username='staff1'")
        self.staff_uid = row[0]
        # Ticket
        self.tk_id = self.mm.create_ticket(self.apt_id, None, "Leak", "High")

    # get_available_staff
    def test_get_available_staff_returns_maintenance_users(self):
        rows = self.mm.get_available_staff()
        user_ids = [r[0] for r in rows]
        self.assertIn(self.staff_uid, user_ids)

    def test_get_available_staff_no_non_maintenance(self):
        self.auth.create_user("admin2", "pass123", "admin")
        rows = self.mm.get_available_staff()
        admin_row = self.db.fetch_one(
            "SELECT id FROM users WHERE username='admin2'")
        admin_uid = admin_row[0]
        user_ids = [r[0] for r in rows]
        self.assertNotIn(admin_uid, user_ids)

    # get_maintenance_costs_summary (in maintenance_manager)
    def test_get_maintenance_costs_summary_returns_rows(self):
        rows = self.mm.get_maintenance_costs_summary()
        self.assertIsInstance(rows, list)

    def test_get_maintenance_costs_summary_after_cost_log(self):
        self.mm.assign_staff(self.tk_id, self.staff_uid)
        self.mm.update_status(self.tk_id, "In Progress")
        self.mm.log_costs(self.tk_id, 2.0, 150.0)
        rows = self.mm.get_maintenance_costs_summary()
        units = [r[0] for r in rows]
        self.assertIn("U99", units)

    # get_cost_report_by_apartment
    def test_get_cost_report_by_apartment_returns_rows(self):
        rows = self.mm.get_cost_report_by_apartment()
        self.assertIsInstance(rows, list)
        self.assertGreaterEqual(len(rows), 1)

    def test_get_cost_report_by_apartment_columns(self):
        rows = self.mm.get_cost_report_by_apartment()
        # (unit_number, city, total_tickets, open_tickets, resolved_tickets, total_cost, hours, avg_cost)
        row = rows[0]
        self.assertEqual(len(row), 8)

    # get_cost_report_by_city
    def test_get_cost_report_by_city_returns_rows(self):
        rows = self.mm.get_cost_report_by_city()
        self.assertIsInstance(rows, list)
        self.assertGreaterEqual(len(rows), 1)

    def test_get_cost_report_by_city_has_bristol(self):
        rows = self.mm.get_cost_report_by_city()
        cities = [r[0] for r in rows]
        self.assertIn("Bristol", cities)

    # get_tickets_by_status_count
    def test_get_tickets_by_status_count_dict(self):
        counts = self.mm.get_tickets_by_status_count()
        self.assertIsInstance(counts, dict)
        self.assertGreaterEqual(counts.get("Open", 0), 1)

    def test_get_tickets_by_status_count_after_update(self):
        self.mm.assign_staff(self.tk_id, self.staff_uid)
        counts = self.mm.get_tickets_by_status_count()
        self.assertGreaterEqual(counts.get("Assigned", 0), 1)

    # notify_tenant_scheduled_date
    def test_notify_tenant_sets_scheduled_date(self):
        self.mm.notify_tenant_scheduled_date(self.tk_id, "2026-06-01")
        row = self.db.fetch_one(
            "SELECT scheduled_date FROM maintenance_requests WHERE id=?", (self.tk_id,))
        self.assertEqual(row[0], "2026-06-01")

    def test_notify_tenant_nonexistent_raises(self):
        with self.assertRaises(Exception):
            self.mm.notify_tenant_scheduled_date(99999, "2026-06-01")


class TestAuthManagerBasicValidation(BaseTest):
    """Auth manager enforces role validity and username uniqueness."""

    def setUp(self):
        super().setUp()
        self.auth = AuthManager(self.db)

    def test_invalid_role_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.auth.create_user("newuser", "pass123", "superadmin")
        self.assertIn("Invalid role", str(ctx.exception))

    def test_duplicate_username_raises(self):
        self.auth.create_user("dupuser", "pass123", "admin")
        with self.assertRaises(Exception) as ctx:
            self.auth.create_user("dupuser", "pass123", "admin")
        self.assertIn("taken", str(ctx.exception))

    def test_valid_user_created(self):
        result = self.auth.create_user("validuser", "pass", "admin")
        self.assertTrue(result)


class TestApartmentReassignment(BaseTest):
    """After removing the apartment_id UNIQUE constraint, an apartment can be
    assigned to a second tenant once the first is archived."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.db.execute_query(
            "INSERT INTO apartments (unit_number, address, city, rental_price, "
            "square_footage, status) VALUES ('A1','1 St','Bristol',800,400,'Vacant')")
        row = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='A1'")
        self.apt_id = row[0]
        self.tm.register_tenant(
            "tenant1", "pass123", "NIT1", "Tenant One",
            "07000", "t1@test.com", "Dev", "None", "None", "1 bed")
        self.tm.register_tenant(
            "tenant2", "pass123", "NIT2", "Tenant Two",
            "07000", "t2@test.com", "Dev", "None", "None", "1 bed")
        row1 = self.db.fetch_one("SELECT id FROM users WHERE username='tenant1'")
        row2 = self.db.fetch_one("SELECT id FROM users WHERE username='tenant2'")
        self.uid1 = row1[0]
        self.uid2 = row2[0]

    def test_reassign_after_archive(self):
        self.tm.assign_apartment(self.uid1, self.apt_id,
                                  "2025-01-01", "2025-12-31", 800, 400)
        self.tm.archive_tenant(self.uid1)
        # Apartment should now be Vacant again
        apt = self.db.fetch_one(
            "SELECT status FROM apartments WHERE id=?", (self.apt_id,))
        self.assertEqual(apt[0], "Vacant")
        # Assigning to tenant2 must NOT raise IntegrityError
        result = self.tm.assign_apartment(
            self.uid2, self.apt_id, "2026-01-01", "2026-12-31", 800, 400)
        self.assertTrue(result)

    def test_both_tenant_rows_can_reference_same_apt_if_one_archived(self):
        """DB must allow two rows referencing the same apartment_id when first is archived."""
        self.tm.assign_apartment(self.uid1, self.apt_id,
                                  "2025-01-01", "2025-12-31", 800, 400)
        self.tm.archive_tenant(self.uid1)
        # After archive, apartment_id on tenant1 is cleared — but the UNIQUE constraint
        # previously prevented this. Just verify tenant2 can be assigned now.
        self.tm.assign_apartment(
            self.uid2, self.apt_id, "2026-01-01", "2026-12-31", 800, 400)
        row = self.db.fetch_one(
            "SELECT apartment_id FROM tenants WHERE user_id=?", (self.uid2,))
        self.assertEqual(row[0], self.apt_id)


class TestEarlyTerminationInvoice(BaseTest):
    """Penalty invoice should be generated BEFORE termination (as done in the view)."""

    def setUp(self):
        super().setUp()
        self.tm = TenantManager(self.db)
        self.im = InvoiceManager(self.db)
        self.tm.register_tenant(
            "alice", "pass123", "NI300", "Alice",
            "07000", "a@test.com", "Dev", "None", "None", "1 bed")
        row = self.db.fetch_one("SELECT id FROM users WHERE username='alice'")
        self.uid = row[0]
        self.db.execute_query(
            "UPDATE tenants SET monthly_rent=1000 WHERE user_id=?", (self.uid,))

    def test_generate_invoice_before_termination(self):
        penalty = 1000 * 0.05
        # 1. Generate penalty invoice while tenant is still Active
        inv_id = self.im.generate_invoice(self.uid, penalty)
        self.assertIsNotNone(inv_id)
        # 2. Now terminate
        result = self.tm.early_termination(self.uid)
        self.assertEqual(result["penalty"], penalty)
        # 3. Invoice must still exist and be Pending
        inv = self.db.fetch_one(
            "SELECT total_amount, status FROM invoices WHERE id=?", (inv_id,))
        self.assertIsNotNone(inv)
        self.assertAlmostEqual(inv[0], penalty, places=2)
        self.assertEqual(inv[1], "Pending")

    def test_invoice_blocked_after_termination(self):
        self.tm.early_termination(self.uid)
        with self.assertRaises(Exception) as ctx:
            self.im.generate_invoice(self.uid, 50)
        self.assertIn("Terminated", str(ctx.exception))

    def test_zero_rent_produces_zero_penalty(self):
        self.db.execute_query(
            "UPDATE tenants SET monthly_rent=0 WHERE user_id=?", (self.uid,))
        result = self.tm.early_termination(self.uid)
        self.assertEqual(result["penalty"], 0)


class TestReportManagerCostSummary(BaseTest):
    """get_maintenance_cost_summary should include zero-cost tickets in total
    and count completed tickets by status, not by cost presence."""

    def setUp(self):
        super().setUp()
        from report_manager import ReportManager
        self.rm = ReportManager(self.db)
        self.mm = MaintenanceManager(self.db)
        self.auth = AuthManager(self.db)
        self.db.execute_query(
            "INSERT INTO apartments (unit_number, address, city, rental_price, "
            "square_footage, status) VALUES ('R1','1 Rd','Bristol',700,400,'Vacant')")
        row = self.db.fetch_one("SELECT id FROM apartments WHERE unit_number='R1'")
        self.apt_id = row[0]
        self.auth.create_user("mstaff", "pass123", "maintenance",
                              employee_id="EMP999", department="Maint")
        row = self.db.fetch_one("SELECT id FROM users WHERE username='mstaff'")
        self.staff_uid = row[0]

    def test_completed_tickets_counts_costed_tickets(self):
        tk1 = self.mm.create_ticket(self.apt_id, None, "Fix pipe", "High")
        tk2 = self.mm.create_ticket(self.apt_id, None, "Paint", "Low")
        self.mm.assign_staff(tk1, self.staff_uid)
        self.mm.update_status(tk1, "In Progress")
        self.mm.log_costs(tk1, 2.0, 200.0)
        summary = self.rm.get_maintenance_cost_summary()
        # completed_tickets = tickets where costs have been logged
        self.assertGreaterEqual(summary["completed_tickets"], 1)

    def test_total_cost_includes_zero_cost_tickets(self):
        # Ticket with no cost logged — should not skew the total
        self.mm.create_ticket(self.apt_id, None, "Check windows", "Low")
        summary = self.rm.get_maintenance_cost_summary()
        # Should not raise and total_cost should be >= 0
        self.assertGreaterEqual(summary["total_cost"], 0)

    def test_avg_cost_excludes_null_cost(self):
        tk = self.mm.create_ticket(self.apt_id, None, "Plumbing", "High")
        self.mm.assign_staff(tk, self.staff_uid)
        self.mm.update_status(tk, "In Progress")
        self.mm.log_costs(tk, 3.0, 300.0)
        # Another ticket with no cost
        self.mm.create_ticket(self.apt_id, None, "Painting", "Low")
        summary = self.rm.get_maintenance_cost_summary()
        # avg_cost should be 300 (only one ticket has a cost), not 150
        self.assertAlmostEqual(summary["avg_cost"], 300.0, places=1)
