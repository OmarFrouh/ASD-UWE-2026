import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="pams.db"):
        self.db_name = db_name
 
    def get_connection(self):
        """Returns a database connection."""
        return sqlite3.connect(self.db_name)

    def execute_query(self, query, params=()):
        """Executes a query that changes data (CREATE, INSERT, UPDATE, DELETE)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Executes a query and returns all results (SELECT)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return []

    def fetch_one(self, query, params=()):
        """Executes a query and returns a single result (SELECT)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

    def create_tables(self):
        """Creates the initial database schema based on SYSTEM_DESIGN.md."""
        
        # 1. Users Table (Base for Admin, Staff, Tenant)
        # Stores authentication and role data.
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT,
                last_login TEXT
            );
        """)

        # 2. Staff Details (Linked to Users)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS staff (
                user_id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                department TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 3. Apartments Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT UNIQUE NOT NULL,
                address TEXT,
                rental_price REAL,
                square_footage INTEGER,
                status TEXT DEFAULT 'Vacant'
            );
        """)

        # 4. Tenants Details (Linked to Users and Apartments)
        # Includes apartment_id FK to link Tenant -> Apartment (1:1 optional)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tenants (
                user_id INTEGER PRIMARY KEY,
                apartment_id INTEGER UNIQUE,
                full_name TEXT NOT NULL,
                email TEXT,
                phone_number TEXT,
                emergency_contact TEXT,
                lease_start_date TEXT,
                lease_end_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE SET NULL
            );
        """)

        # 5. Maintenance Requests
        # Linked to Apartment (History) and Staff (Assignment)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER NOT NULL,
                staff_id INTEGER,
                description TEXT NOT NULL,
                priority TEXT,
                status TEXT DEFAULT 'Open',
                date_reported TEXT,
                date_resolved TEXT,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE CASCADE,
                FOREIGN KEY (staff_id) REFERENCES staff (user_id) ON DELETE SET NULL
            );
        """)

        # 6. Invoices
        # Linked to Tenant
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                issue_date TEXT,
                due_date TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id) ON DELETE CASCADE
            );
        """)

        # 7. Payments
        # Linked to Invoice (Composition)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL,
                payment_date TEXT,
                method TEXT,
                transaction_ref TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            );
        """)

        print("✅ Database schema created successfully.")

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_tables()
