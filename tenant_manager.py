# Student Name: Feras Bader
# Student ID: 24033513

import bcrypt
from datetime import datetime, timedelta

EARLY_TERMINATION_PENALTY_RATE = 0.05

class TenantManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def register_tenant(self, username, password, ni_number, full_name, phone, email, occupation, references, emergency_contact, apt_requirements):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt).decode('utf-8')

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed, "tenant")
            )
            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO tenants (user_id, ni_number, full_name, phone_number, email,
                    occupation, references_info, emergency_contact, apartment_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, ni_number, full_name, phone, email, occupation, references, emergency_contact, apt_requirements))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all_tenants(self):
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
            ORDER BY t.full_name
        """)

    def get_archived_tenants(self):
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.status
            FROM tenants t WHERE t.status IN ('Archived', 'Terminated')
        """)

    def assign_apartment(self, tenant_user_id, apartment_id, lease_start, lease_end, monthly_rent, deposit):
        # Validate tenant exists and is active
        tenant = self.db_manager.fetch_one("SELECT user_id, status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[1] in ("Terminated", "Archived"):
            raise Exception(f"Cannot assign apartment to a {tenant[1]} tenant")

        # Validate apartment exists and is vacant
        apt = self.db_manager.fetch_one("SELECT id, status FROM apartments WHERE id=?", (apartment_id,))
        if not apt:
            raise Exception("Apartment not found")
        if apt[1] != "Vacant":
            raise Exception("Apartment is already occupied")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE tenants SET apartment_id=?, lease_start_date=?, lease_end_date=?,
                    monthly_rent=?, deposit_amount=? WHERE user_id=?
            """, (apartment_id, lease_start, lease_end, monthly_rent, deposit, tenant_user_id))
            cursor.execute("UPDATE apartments SET status='Occupied' WHERE id=?", (apartment_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()



    def reactivate_tenant(self, tenant_user_id):
        tenant = self.db_manager.fetch_one(
            "SELECT status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[0] == "Terminated":
            raise Exception("Cannot reactivate a Terminated tenant.")
        if tenant[0] == "Active":
            raise Exception("Tenant is already Active.")
        self.db_manager.execute_query(
            "UPDATE tenants SET status='Active' WHERE user_id=?", (tenant_user_id,))
        return True

    def archive_tenant(self, tenant_user_id):
        tenant = self.db_manager.fetch_one(
            "SELECT apartment_id, status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[1] == "Archived":
            raise Exception("Tenant is already Archived")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tenants SET status='Archived', apartment_id=NULL WHERE user_id=?",
                (tenant_user_id,))
            if tenant[0]:
                cursor.execute("UPDATE apartments SET status='Vacant' WHERE id=?", (tenant[0],))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def search_tenants(self, query):
        """Search tenants by name, NI number, email, or phone.
        Returns: list matching the same format as get_all_tenants()"""
        search = f"%{query}%"
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = 'Active'
              AND (t.full_name LIKE ? OR t.ni_number LIKE ? OR t.email LIKE ? OR t.phone_number LIKE ?)
            ORDER BY t.full_name
        """, (search, search, search, search))

    def filter_tenants_by_status(self, status):
        """Filter tenants by status (Active, Archived, Terminated, All).
        Returns: list matching the same format as get_all_tenants()"""
        if status == "All":
            return self.db_manager.fetch_all("""
                SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                       t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                       t.monthly_rent, t.status, a.unit_number
                FROM tenants t
                LEFT JOIN apartments a ON t.apartment_id = a.id
                ORDER BY t.full_name
            """)
        return self.db_manager.fetch_all("""
            SELECT t.user_id, t.ni_number, t.full_name, t.phone_number, t.email,
                   t.occupation, t.apartment_id, t.lease_start_date, t.lease_end_date,
                   t.monthly_rent, t.status, a.unit_number
            FROM tenants t
            LEFT JOIN apartments a ON t.apartment_id = a.id
            WHERE t.status = ?
            ORDER BY t.full_name
        """, (status,))

    def get_tenant_count_by_status(self):
        """Returns dict with counts per status for dashboard display."""
        rows = self.db_manager.fetch_all("""
            SELECT status, COUNT(*) FROM tenants GROUP BY status
        """)
        return {row[0]: row[1] for row in rows}


    def early_termination(self, tenant_user_id):
        """Processes early lease termination with 1-month notice and 5% penalty.
        Returns a dict with 'penalty' and 'effective_date' (YYYY-MM-DD)."""
        tenant = self.db_manager.fetch_one(
            "SELECT monthly_rent, apartment_id, status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[2] in ("Terminated", "Archived"):
            raise Exception(f"Tenant is already {tenant[2]}")
        penalty = (tenant[0] or 0) * EARLY_TERMINATION_PENALTY_RATE
        notice_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tenants SET status='Terminated', lease_end_date=?, apartment_id=NULL WHERE user_id=?",
                (notice_end, tenant_user_id))
            if tenant[1]:
                cursor.execute("UPDATE apartments SET status='Vacant' WHERE id=?", (tenant[1],))
            conn.commit()
            return {"penalty": penalty, "effective_date": notice_end}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_tenant_by_id(self, tenant_user_id):
        """Returns all fields for a single tenant for edit form pre-fill."""
        return self.db_manager.fetch_one(
            """
            SELECT user_id, ni_number, full_name, phone_number, email,
                   occupation, references_info, emergency_contact, apartment_requirements,
                   apartment_id, lease_start_date, lease_end_date, monthly_rent, deposit_amount, status
            FROM tenants WHERE user_id=?
            """,
            (tenant_user_id,)
        )

    def update_tenant(self, tenant_user_id, full_name=None, phone=None, email=None,
                      occupation=None, references=None, emergency_contact=None, apt_requirements=None):
        """Updates editable tenant fields; non-None values are changed."""
        tenant = self.db_manager.fetch_one(
            "SELECT user_id, status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[1] in ("Terminated", "Archived"):
            raise Exception(f"Cannot update a {tenant[1]} tenant")
        updates = []
        params = []
        field_map = {
            "full_name": full_name,
            "phone_number": phone,
            "email": email,
            "occupation": occupation,
            "references_info": references,
            "emergency_contact": emergency_contact,
            "apartment_requirements": apt_requirements,
        }
        for col, val in field_map.items():
            if val is not None:
                updates.append(f"{col}=?")
                params.append(val)
        if not updates:
            raise Exception("No fields to update")
        params.append(tenant_user_id)
        self.db_manager.execute_query(
            f"UPDATE tenants SET {', '.join(updates)} WHERE user_id=?",
            tuple(params)
        )
        return True

    def log_complaint(self, tenant_id, subject, description):
        """Logs a new complaint for a tenant."""
        tenant = self.db_manager.fetch_one(
            "SELECT user_id FROM tenants WHERE user_id=?", (tenant_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if not subject or not description:
            raise Exception("Subject and description are required")
        self.db_manager.execute_query(
            """
            INSERT INTO complaints (tenant_id, date_logged, subject, description, status)
            VALUES (?, ?, ?, ?, 'Open')
            """,
            (tenant_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), subject, description)
        )
        return True

    def get_all_complaints(self):
        """Returns all complaints with tenant info for the Complaints tab."""
        return self.db_manager.fetch_all(
            """
            SELECT c.id, t.full_name, c.subject, c.date_logged, c.status, c.description
            FROM complaints c
            JOIN tenants t ON c.tenant_id = t.user_id
            ORDER BY c.date_logged DESC
            """
        )






    def get_complaints_for_tenant(self, tenant_id):
        """Returns all complaints for a specific tenant.
        Returns: list of (id, date_logged, subject, description, status, resolved_date)"""
        return self.db_manager.fetch_all("""
            SELECT id, date_logged, subject, description, status, resolved_date
            FROM complaints WHERE tenant_id=?
            ORDER BY date_logged DESC
        """, (tenant_id,))



    def resolve_complaint(self, complaint_id):
        """Marks a complaint as resolved with today's date."""
        complaint = self.db_manager.fetch_one(
            "SELECT id, status FROM complaints WHERE id=?", (complaint_id,))
        if not complaint:
            raise Exception("Complaint not found")
        if complaint[1] == "Resolved":
            raise Exception("Complaint is already resolved")

        self.db_manager.execute_query(
            "UPDATE complaints SET status='Resolved', resolved_date=? WHERE id=?",
            (datetime.now().strftime("%Y-%m-%d"), complaint_id))
        return True
