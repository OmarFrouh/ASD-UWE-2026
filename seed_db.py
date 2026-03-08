from database_manager import DatabaseManager
from auth_manager import AuthManager

def seed():
    print("🌱 Seeding Database...")
    db = DatabaseManager("pams.db")
    
    # Ensure table exists first (just in case)
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL,
        role TEXT NOT NULL
    );
    """)

    auth = AuthManager(db)
    
    try:
        # Create Admin
        auth.create_user("admin", "admin123", "admin")
        print("✅ Admin user created (admin / admin123)")
    except Exception as e:
        print(f"⚠️ Could not create user (might already exist): {e}")

if __name__ == "__main__":
    seed()
