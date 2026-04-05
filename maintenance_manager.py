# Student Name: Numair
# Student ID: 24026758

from datetime import datetime

class MaintenanceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_ticket(self, apartment_id, tenant_id, description, priority="Medium"):
        if not description:
            raise Exception("Description is required")
        if priority not in ["Low", "Medium", "High", "Urgent"]:
            raise Exception("Priority must be Low, Medium, High, or Urgent")

        # Validate apartment exists
        apt = self.db_manager.fetch_one("SELECT id FROM apartments WHERE id=?", (apartment_id,))
        if not apt:
            raise Exception("Apartment not found")

        self.db_manager.execute_query("""
            INSERT INTO maintenance_requests
                (apartment_id, tenant_id, description, priority, status, date_reported)
            VALUES (?, ?, ?, ?, 'Open', ?)
        """, (apartment_id, tenant_id or None, description, priority,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True

    def get_all_tickets(self):
        return self.db_manager.fetch_all("""
            SELECT m.id, a.unit_number, t.full_name, m.description, m.priority,
                   m.status, m.date_reported, m.scheduled_date,
                   s_user.username AS assigned_to, m.time_spent, m.cost
            FROM maintenance_requests m
            LEFT JOIN apartments a ON m.apartment_id = a.id
            LEFT JOIN tenants t ON m.tenant_id = t.user_id
            LEFT JOIN staff st ON m.staff_id = st.user_id
            LEFT JOIN users s_user ON st.user_id = s_user.id
            ORDER BY
                CASE m.priority
                    WHEN 'Urgent' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                END, m.date_reported DESC
        """)

    def assign_staff(self, ticket_id, staff_user_id, scheduled_date=None):
        # Validate ticket exists
        ticket = self.db_manager.fetch_one("SELECT id FROM maintenance_requests WHERE id=?", (ticket_id,))
        if not ticket:
            raise Exception("Ticket not found")

        staff = self.db_manager.fetch_one(
            "SELECT user_id FROM staff WHERE user_id=?", (staff_user_id,))
        if not staff:
            raise Exception("Staff member not found")

        self.db_manager.execute_query("""
            UPDATE maintenance_requests
            SET staff_id=?, scheduled_date=?, status='Assigned'
            WHERE id=?
        """, (staff_user_id, scheduled_date, ticket_id))
        return True

    def update_status(self, ticket_id, new_status):
        valid = ["Open", "Assigned", "In Progress", "Fixed", "Closed"]
        if new_status not in valid:
            raise Exception(f"Status must be one of: {', '.join(valid)}")

        # Validate ticket exists and get current status
        ticket = self.db_manager.fetch_one(
            "SELECT id, status FROM maintenance_requests WHERE id=?", (ticket_id,))
        if not ticket:
            raise Exception("Ticket not found")

        # Enforce valid status transitions
        transitions = {
            "Open": ["Assigned", "In Progress", "Closed"],
            "Assigned": ["In Progress", "Closed"],
            "In Progress": ["Fixed", "Closed"],
            "Fixed": ["Closed"],
            "Closed": [],
        }
        current_status = ticket[1]
        if new_status not in transitions.get(current_status, []):
            raise Exception(f"Cannot transition from '{current_status}' to '{new_status}'")

        if new_status == "Fixed":
            self.db_manager.execute_query(
                "UPDATE maintenance_requests SET status=?, date_resolved=? WHERE id=?",
                (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ticket_id))
        else:
            self.db_manager.execute_query(
                "UPDATE maintenance_requests SET status=? WHERE id=?",
                (new_status, ticket_id))
        return True

    def log_costs(self, ticket_id, time_spent, cost):
        # Validate ticket exists
        ticket = self.db_manager.fetch_one("SELECT id FROM maintenance_requests WHERE id=?", (ticket_id,))
        if not ticket:
            raise Exception("Ticket not found")

        try:
            time_spent = float(time_spent)
            cost = float(cost)
        except ValueError:
            raise Exception("Time and cost must be valid numbers")

        if time_spent < 0 or cost < 0:
            raise Exception("Time and cost must be positive")

        self.db_manager.execute_query("""
            UPDATE maintenance_requests 
            SET time_spent = COALESCE(time_spent, 0) + ?, 
                cost = COALESCE(cost, 0) + ? 
            WHERE id=?
        """, (time_spent, cost, ticket_id))
        return True

    def get_available_staff(self):
        return self.db_manager.fetch_all("""
            SELECT s.user_id, u.username, s.department
            FROM staff s JOIN users u ON s.user_id = u.id
            WHERE u.role = 'maintenance'
        """)

    def get_maintenance_costs_summary(self):
        return self.db_manager.fetch_all("""
            SELECT a.unit_number, COUNT(*) as total_tickets,
                   COALESCE(SUM(m.cost), 0) as total_cost,
                   COALESCE(SUM(m.time_spent), 0) as total_hours
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.id
            GROUP BY a.unit_number
        """)
