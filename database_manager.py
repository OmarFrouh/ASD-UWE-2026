# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import sqlite3

class DatabaseManager:
    def __init__(self, db_name="pams.db"):
        self.db_name = db_name

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def execute_query(self, query, params=()):
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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return []

    def fetch_one(self, query, params=()):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

    def create_tables(self):
        # 1. Users
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            );
        """)

        # 2. Staff
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS staff (
                user_id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                department TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 3. Apartments (Updated: city, number_of_rooms)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT UNIQUE NOT NULL,
                address TEXT,
                city TEXT DEFAULT 'Bristol',
                number_of_rooms INTEGER DEFAULT 1,
                rental_price REAL,
                square_footage INTEGER,
                status TEXT DEFAULT 'Vacant'
            );
        """)

        # 4. Tenants (Updated: NI, occupation, references, etc.)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS tenants (
                user_id INTEGER PRIMARY KEY,
                ni_number TEXT UNIQUE,
                full_name TEXT NOT NULL,
                phone_number TEXT,
                email TEXT,
                occupation TEXT,
                references_info TEXT,
                emergency_contact TEXT,
                apartment_requirements TEXT,
                apartment_id INTEGER UNIQUE,
                lease_start_date TEXT,
                lease_end_date TEXT,
                deposit_amount REAL,
                monthly_rent REAL,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE SET NULL
            );
        """)

        # 5. Maintenance Requests (Updated: tenant_id, costs, scheduling)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER NOT NULL,
                tenant_id INTEGER,
                staff_id INTEGER,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                date_reported TEXT DEFAULT CURRENT_TIMESTAMP,
                scheduled_date TEXT,
                date_resolved TEXT,
                time_spent REAL,
                cost REAL,
                FOREIGN KEY (apartment_id) REFERENCES apartments (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id) ON DELETE SET NULL,
                FOREIGN KEY (staff_id) REFERENCES staff (user_id) ON DELETE SET NULL
            );
        """)

        # 6. Invoices
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                issue_date TEXT,
                due_date TEXT,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id) ON DELETE CASCADE
            );
        """)

        # 7. Payments
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT,
                method TEXT,
                transaction_ref TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            );
        """)

        # 8. Complaints (Sprint 3)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                date_logged TEXT DEFAULT CURRENT_TIMESTAMP,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                resolved_date TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants (user_id) ON DELETE CASCADE
            );
        """)

        print("✅ Database schema created successfully.")

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_tables()
