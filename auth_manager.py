# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import bcrypt

VALID_ROLES = ["admin", "staff", "front_desk", "finance_manager", "maintenance", "manager", "tenant"]

class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username=?"
        user_record = self.db_manager.fetch_one(query, (username,))

        if not user_record:
            return None

        stored_hash = user_record[2]
        if self.verify_hash(password, stored_hash):
            self.db_manager.execute_query(
                "UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?", (user_record[0],))
            return user_record
        return None

    def verify_hash(self, plain_password, hashed_password):
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def create_user(self, username, password, role="staff", employee_id=None, department=None):
        # Validate role
        if role not in VALID_ROLES:
            raise Exception(f"Invalid role '{role}'. Must be one of: {', '.join(VALID_ROLES)}")

        # Prevent raw SQLite Integrity error by checking explicitly
        existing = self.db_manager.fetch_one("SELECT id FROM users WHERE username=?", (username,))
        if existing:
            raise Exception("Username is already taken.")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            new_user_id = cursor.lastrowid

            if role in ["staff", "manager", "maintenance", "front_desk", "finance_manager"]:
                if not employee_id:
                    raise Exception("Employee ID is required for staff roles.")
                cursor.execute(
                    "INSERT INTO staff (user_id, employee_id, department) VALUES (?, ?, ?)",
                    (new_user_id, employee_id, department)
                )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_dashboard_stats(self):
        stats = {}
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                stats["Total Users"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM staff")
                stats["Total Staff"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM apartments")
                stats["Apartments"] = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM apartments WHERE status='Vacant'")
                stats["Vacant"] = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {}
        return stats
