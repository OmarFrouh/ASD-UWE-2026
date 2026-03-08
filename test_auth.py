from database_manager import DatabaseManager
from auth_manager import AuthManager
import os

# Setup
db = DatabaseManager("test_pams.db") # Use a separate test DB to avoid messing up real data
# Initialize tables for test DB (since it's new)
# We can just run the schema creation query directly or assume it exists. 
# Better to create it fresh.
schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    role TEXT NOT NULL
);
"""
db.execute_query(schema)

auth = AuthManager(db)

print("--- Starting Auth Test ---")

# 1. Create a User
print("Step 1: Creating Admin User...")
try:
    auth.create_user("admin", "admin123", "admin")
except Exception as e:
    print(f"Make sure to clean up DB or ignore if exists: {e}")

# 2. Test Success
print("\nStep 2: Testing Valid Login...")
user = auth.login("admin", "admin123")
if user:
    print("✅ SUCCESS: Login approved for 'admin'.")
else:
    print("❌ FAILURE: Could not log in with correct password.")

# 3. Test Failure (Wrong Password)
print("\nStep 3: Testing Invalid Password...")
user = auth.login("admin", "wrongpass")
if not user:
    print("✅ SUCCESS: Login rejected for wrong password.")
else:
    print("❌ FAILURE: Login accepted wrong password!")

# 4. Test Failure (Wrong Username)
print("\nStep 4: Testing Non-existent User...")
user = auth.login("ghost", "password")
if not user:
    print("✅ SUCCESS: Login rejected for unknown user.")
else:
    print("❌ FAILURE: Login accepted unknown user!")

# Cleanup (Optional)
os.remove("test_pams.db")
print("\n--- Test Complete ---")
