# Student Name: Feras Bader
# Student ID: 24033513

import bcrypt
from datetime import datetime

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

    def early_termination(self, tenant_user_id):
        tenant = self.db_manager.fetch_one(
            "SELECT monthly_rent, apartment_id, status FROM tenants WHERE user_id=?", (tenant_user_id,))
        if not tenant:
            raise Exception("Tenant not found")
        if tenant[2] in ("Terminated", "Archived"):
            raise Exception(f"Tenant is already {tenant[2]}")

        penalty = (tenant[0] or 0) * EARLY_TERMINATION_PENALTY_RATE
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tenants SET status='Terminated', lease_end_date=?, apartment_id=NULL WHERE user_id=?",
                (datetime.now().strftime("%Y-%m-%d"), tenant_user_id))
            if tenant[1]:
                cursor.execute("UPDATE apartments SET status='Vacant' WHERE id=?", (tenant[1],))
            conn.commit()
            return penalty
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

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
