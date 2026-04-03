import unittest
from tests.test_base import BaseTest
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager
from tenant_manager import TenantManager

class TestFinance(BaseTest):
    def setUp(self):
        super().setUp()
        self.inv = InvoiceManager(self.db)
        self.pay = PaymentManager(self.db)
        self.tenant = TenantManager(self.db)
        
        # Setup tenant
        self.tenant.register_tenant("finance_guy", "pass", "NIFIN", "Finance Guy", "", "", "", "", "", "")
        self.user_id = self.db.fetch_one("SELECT id FROM users")[0]
        # Inject an apartment directly for speed
        self.db.execute_query("INSERT INTO apartments (unit_number, rental_price) VALUES ('F100', 1200)")
        self.apt_id = self.db.fetch_one("SELECT id FROM apartments")[0]
        self.tenant.assign_apartment(self.user_id, self.apt_id, "2026-01-01", "2026-12-31", 1200.0, 500.0)

    def test_invoice_generation_defaults_to_rent(self):
        self.inv.generate_invoice(self.user_id)
        
        invoices = self.inv.get_all_invoices()
        self.assertEqual(len(invoices), 1)
        # Check amount defaults to rent (1200)
        self.assertEqual(invoices[0][4], 1200.0)
        self.assertEqual(invoices[0][5], "Pending")

    def test_cannot_invoice_terminated_tenant(self):
        self.tenant.early_termination(self.user_id)
        
        with self.assertRaises(Exception) as ctx:
            self.inv.generate_invoice(self.user_id, 500)
        self.assertIn("Cannot invoice a Terminated tenant", str(ctx.exception))

    def test_payment_updates_invoice_status(self):
        self.inv.generate_invoice(self.user_id, 1000)
        inv_id = self.inv.get_all_invoices()[0][0]
        
        # Pay partial amount
        self.pay.record_payment(inv_id, 400, "Cash")
        invoice = self.db.fetch_one("SELECT status FROM invoices WHERE id=?", (inv_id,))
        self.assertEqual(invoice[0], "Pending")
        
        # Pay remaining amount
        self.pay.record_payment(inv_id, 600, "Bank Transfer")
        invoice = self.db.fetch_one("SELECT status FROM invoices WHERE id=?", (inv_id,))
        self.assertEqual(invoice[0], "Paid")

    def test_cannot_pay_already_paid_invoice(self):
        self.inv.generate_invoice(self.user_id, 100)
        inv_id = self.inv.get_all_invoices()[0][0]
        
        self.pay.record_payment(inv_id, 100, "Cash")
        
        with self.assertRaises(Exception) as ctx:
            self.pay.record_payment(inv_id, 50, "Cash")
        self.assertIn("Invoice already paid", str(ctx.exception))

    def test_negative_payment_fails(self):
        self.inv.generate_invoice(self.user_id, 100)
        inv_id = self.inv.get_all_invoices()[0][0]
        with self.assertRaises(Exception) as ctx:
            self.pay.record_payment(inv_id, -50, "Cash")
        self.assertIn("Amount must be positive", str(ctx.exception))

    def test_cannot_invoice_archived_tenant(self):
        self.tenant.archive_tenant(self.user_id)
        with self.assertRaises(Exception) as ctx:
            self.inv.generate_invoice(self.user_id, 500)
        self.assertIn("Cannot invoice a Archived tenant", str(ctx.exception))

    def test_overpayment_rejected(self):
        self.inv.generate_invoice(self.user_id, 100)
        inv_id = self.inv.get_all_invoices()[0][0]
        with self.assertRaises(Exception) as ctx:
            self.pay.record_payment(inv_id, 150, "Cash")
        self.assertIn("exceeds remaining balance", str(ctx.exception))
