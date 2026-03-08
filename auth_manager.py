import bcrypt
from database_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_manager):
        """
        Initializes the AuthManager with a DatabaseManager instance.
        """
        self.db_manager = db_manager

    def login(self, username, password):
        """
        Authenticates a user by checking username and password.
        Returns the user record (dict/tuple) if successful, None if failed.
        """
        # Step 1: Fetch the user record from the database
        # (Matches Sequence Diagram Arrow 3)
        query = "SELECT * FROM users WHERE username=?"
        user_record = self.db_manager.fetch_one(query, (username,))

        # Step 2: Check if user exists
        if not user_record:
            return None  # User not found

        # Step 3: Verify the password
        # (Matches Sequence Diagram Loop Arrow)
        # Note: Depending on how fetch_one returns data (tuple or dict), 
        # we need to access the password hash correctly.
        # Assuming fetch_one returns a tuple, and password_hash is at a specific index.
        # However, for robustness, we should know the schema.
        # Schema: id, username, password_hash, role
        # password_hash is likely index 2.
        
        # Let's try to handle both tuple and Row factory if we implement that later.
        # For now, based on schema.sql: id, username, password_hash, role
        stored_hash = user_record[2] 
        
        if self.verify_hash(password, stored_hash):
            return user_record # Login Successful
        else:
            return None # Wrong Password

    def verify_hash(self, plain_password, hashed_password):
        """
        Verifies a plain text password against a stored hash using bcrypt.
        """
        # bcrypt requires bytes, so we encode the strings
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def create_user(self, username, password, role="staff", employee_id=None, department=None):
        """
        Creates a new user. If role is staff-related, adds to staff table.
        """
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Transactional Logic
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Insert into Users Table
            query_user = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
            cursor.execute(query_user, (username, hashed_password, role))
            
            # Get the new ID
            new_user_id = cursor.lastrowid
            
            # 2. If Staff, Insert into Staff Table
            if role in ["staff", "manager", "maintenance"]:
                if not employee_id:
                    raise Exception("Employee ID is required for staff roles.")
                
                query_staff = "INSERT INTO staff (user_id, employee_id, department) VALUES (?, ?, ?)"
                cursor.execute(query_staff, (new_user_id, employee_id, department))

            # Commit everything
            conn.commit()
            print(f"User '{username}' created successfully.")
            return True
            
        except Exception as e:
            conn.rollback() # Undo changes if anything failed
            print(f"Error creating user: {e}")
            raise e # Re-raise so UI knows
        finally:
            conn.close()

    def get_dashboard_stats(self):
        """
        Returns a dictionary of system statistics (for the Dashboard).
        (Matches Class Diagram: + get_dashboard_stats() : Map<String, int>)
        """
        stats = {}
        query_users = "SELECT COUNT(*) FROM users"
        
        # We can add more queries here (e.g. Vacant Apartments) as we build them.
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Total Users
                cursor.execute(query_users)
                stats["Total Users"] = cursor.fetchone()[0]
                
                # 2. Total Staff (if needed)
                cursor.execute("SELECT COUNT(*) FROM staff")
                stats["Total Staff"] = cursor.fetchone()[0]
                
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"Error": 0}
            
        return stats
