# Student Name: Omar Alfrouh
# Student ID: 24020879

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

    def get_all_users(self):
        """Returns all users with their staff details where applicable.
        Returns list of (id, username, role, employee_id, department, created_at, last_login)"""
        return self.db_manager.fetch_all("""
            SELECT u.id, u.username, u.role,
                   COALESCE(s.employee_id, ''), COALESCE(s.department, ''),
                   u.created_at, u.last_login
            FROM users u
            LEFT JOIN staff s ON u.id = s.user_id
            ORDER BY u.id
        """)

    def reset_password(self, user_id, new_password):
        if not new_password or len(new_password) < 6:
            raise Exception("Password must be at least 6 characters.")
        user = self.db_manager.fetch_one(
            "SELECT id FROM users WHERE id=?", (user_id,))
        if not user:
            raise Exception("User not found.")
        salt   = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")
        self.db_manager.execute_query(
            "UPDATE users SET password_hash=? WHERE id=?", (hashed, user_id))

    def update_user(self, user_id, role, employee_id, department, current_user_id):
        if user_id == current_user_id:
            raise Exception("Cannot edit your own account here.")

        if role not in VALID_ROLES:
            raise Exception(f"Invalid role '{role}'. Must be one of: {', '.join(VALID_ROLES)}")

        user = self.db_manager.fetch_one(
            "SELECT id, role FROM users WHERE id=?", (user_id,))
        if not user:
            raise Exception("User not found.")

        # Prevent demoting the last admin
        if user[1] == "admin" and role != "admin":
            admin_count = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            )[0]
            if admin_count <= 1:
                raise Exception("Cannot change the role of the only admin account.")

        STAFF_ROLES = {"staff", "manager", "maintenance", "front_desk", "finance_manager"}
        needs_staff = role in STAFF_ROLES
        if needs_staff and not employee_id:
            raise Exception("Employee ID is required for staff roles.")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
            has_staff = cursor.execute(
                "SELECT user_id FROM staff WHERE user_id=?", (user_id,)
            ).fetchone()
            if needs_staff:
                if has_staff:
                    cursor.execute(
                        "UPDATE staff SET employee_id=?, department=? WHERE user_id=?",
                        (employee_id, department, user_id))
                else:
                    cursor.execute(
                        "INSERT INTO staff (user_id, employee_id, department) VALUES (?,?,?)",
                        (user_id, employee_id, department))
            elif has_staff:
                cursor.execute("DELETE FROM staff WHERE user_id=?", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_user(self, user_id, current_user_id):
        if user_id == current_user_id:
            raise Exception("Cannot delete your own account.")

        user = self.db_manager.fetch_one(
            "SELECT id, role FROM users WHERE id=?", (user_id,))
        if not user:
            raise Exception("User not found.")

        if user[1] == "admin":
            admin_count = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM users WHERE role='admin'"
            )[0]
            if admin_count <= 1:
                raise Exception("Cannot remove the only admin account.")

        tenant = self.db_manager.fetch_one(
            "SELECT user_id FROM tenants WHERE user_id=?", (user_id,))
        if tenant:
            raise Exception(
                "Cannot delete a user with tenant records. Archive the tenant first.")

        self.db_manager.execute_query("DELETE FROM users WHERE id=?", (user_id,))

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
