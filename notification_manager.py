# Student Name: Omar Alfrouh
# Student ID: 24020879

from datetime import datetime


class NotificationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_overdue_invoices(self):
        """Returns all invoices that are past their due date and still Pending.
        Returns: list of (invoice_id, tenant_name, due_date, amount, days_overdue)"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT i.id, t.full_name, i.due_date, i.total_amount,
                   CAST(julianday(?) - julianday(i.due_date) AS INTEGER) AS days_overdue
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.user_id
            WHERE i.status = 'Pending' AND i.due_date < ?
            ORDER BY days_overdue DESC
        """, (today, today))

    def get_expiring_leases(self, days=30):
        """Returns tenants whose leases expire within the given number of days.
        Returns: list of (tenant_id, name, lease_end_date, apartment_unit, days_remaining)"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.full_name, t.lease_end_date, a.unit_number,
                   CAST(julianday(t.lease_end_date) - julianday(?) AS INTEGER) AS days_remaining
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
              AND t.lease_end_date IS NOT NULL
              AND julianday(t.lease_end_date) - julianday(?) <= ?
              AND julianday(t.lease_end_date) - julianday(?) >= 0
            ORDER BY days_remaining
        """, (today, today, days, today))

    def get_notification_count(self):
        """Returns total number of active notifications (for badge display)."""
        overdue = len(self.get_overdue_invoices())
        expiring = len(self.get_expiring_leases())
        return overdue + expiring

    def get_notifications(self):
        """Returns all active notifications combined for popup display.
        Returns list of dicts with 'type' and 'text' keys."""
        results = []
        for row in self.get_overdue_invoices():
            # row: (invoice_id, tenant_name, due_date, total_amount, days_overdue)
            invoice_id, name, due_date, amount, days = row
            results.append({
                "type": "overdue",
                "text": f"📄 Invoice #{invoice_id}  |  {name}  |  £{float(amount):.2f}  |  Due: {due_date} ({days} days overdue)"
            })
        for row in self.get_expiring_leases():
            # row: (tenant_id, name, lease_end_date, unit_number, days_remaining)
            _, name, lease_end, unit, days = row
            results.append({
                "type": "expiring",
                "text": f"🏠 Lease expiring  |  {name}  |  Unit {unit}  |  {lease_end} ({days} days left)"
            })
        return results
