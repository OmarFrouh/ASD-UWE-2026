# Student Name: Omar Alfrouh
# Student ID: 24020879


class ReportManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_occupancy_report(self, city=None):
        """Occupancy report filtered by apartment or city.
        Returns: list of (unit_number, address, city, rooms, rent, status)"""
        if city and city != "All":
            return self.db_manager.fetch_all("""
                SELECT unit_number, address, city, number_of_rooms, rental_price, status
                FROM apartments WHERE city = ?
                ORDER BY unit_number
            """, (city,))
        return self.db_manager.fetch_all("""
            SELECT unit_number, address, city, number_of_rooms, rental_price, status
            FROM apartments ORDER BY city, unit_number
        """)

    def get_occupancy_summary(self, city=None):
        """Returns dict with total, occupied, vacant counts."""
        if city and city != "All":
            total = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE city = ?", (city,))[0]
            occupied = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE status = 'Occupied' AND city = ?", (city,))[0]
        else:
            total = self.db_manager.fetch_one("SELECT COUNT(*) FROM apartments")[0]
            occupied = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM apartments WHERE status = 'Occupied'")[0]
        return {
            "total": total,
            "occupied": occupied,
            "vacant": total - occupied,
            "occupancy_rate": round((occupied / total * 100), 1) if total > 0 else 0
        }

    def get_financial_summary(self):
        """Financial summary: collected vs pending rents.
        Returns dict with collected, pending, total_invoiced."""
        collected = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(amount), 0) FROM payments")[0]
        pending = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'Pending'")[0]
        total_invoiced = self.db_manager.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices")[0]
        return {
            "collected": collected,
            "pending": pending,
            "total_invoiced": total_invoiced,
            "collection_rate": round((collected / total_invoiced * 100), 1) if total_invoiced > 0 else 0
        }

    def get_financial_breakdown(self):
        """Per-tenant financial breakdown.
        Returns: list of (tenant_name, total_invoiced, total_paid, outstanding)"""
        return self.db_manager.fetch_all("""
            SELECT t.full_name,
                   COALESCE(SUM(i.total_amount), 0) AS total_invoiced,
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             JOIN invoices i2 ON p.invoice_id = i2.id
                             WHERE i2.tenant_id = t.user_id), 0) AS total_paid,
                   COALESCE(SUM(i.total_amount), 0) -
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             JOIN invoices i2 ON p.invoice_id = i2.id
                             WHERE i2.tenant_id = t.user_id), 0) AS outstanding
            FROM tenants t
            LEFT JOIN invoices i ON t.user_id = i.tenant_id
            WHERE t.status = 'Active'
            GROUP BY t.user_id
            ORDER BY outstanding DESC
        """)

    def get_maintenance_cost_report(self, city=None):
        """Maintenance cost report grouped by apartment.
        Returns: list of (unit_number, city, total_tickets, total_cost, total_hours)"""
        if city and city != "All":
            return self.db_manager.fetch_all("""
                SELECT a.unit_number, a.city,
                       COUNT(m.id) AS total_tickets,
                       COALESCE(SUM(m.cost), 0) AS total_cost,
                       COALESCE(SUM(m.time_spent), 0) AS total_hours
                FROM maintenance_requests m
                JOIN apartments a ON m.apartment_id = a.id
                WHERE a.city = ?
                GROUP BY a.unit_number
                ORDER BY total_cost DESC
            """, (city,))
        return self.db_manager.fetch_all("""
            SELECT a.unit_number, a.city,
                   COUNT(m.id) AS total_tickets,
                   COALESCE(SUM(m.cost), 0) AS total_cost,
                   COALESCE(SUM(m.time_spent), 0) AS total_hours
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.unit_number
            ORDER BY total_cost DESC
        """)

    def get_maintenance_cost_summary(self):
        """Returns dict with total maintenance spend and average cost."""
        result = self.db_manager.fetch_one("""
            SELECT COALESCE(SUM(cost), 0),
                   COALESCE(AVG(CASE WHEN cost IS NOT NULL THEN cost END), 0),
                   COALESCE(SUM(time_spent), 0),
                   COUNT(CASE WHEN cost IS NOT NULL THEN 1 END)
            FROM maintenance_requests
        """)
        return {
            "total_cost": result[0],
            "avg_cost": round(result[1], 2),
            "total_hours": result[2],
            "completed_tickets": result[3]
        }

    def get_cities(self):
        """Returns list of all cities for filter dropdowns."""
        rows = self.db_manager.fetch_all("SELECT DISTINCT city FROM apartments ORDER BY city")
        return [row[0] for row in rows]
