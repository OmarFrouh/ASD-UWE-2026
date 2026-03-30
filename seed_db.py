# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import bcrypt, os
from database_manager import DatabaseManager

def seed():
    db = DatabaseManager("pams.db")
    db.create_tables()
    conn = db.get_connection()
    cursor = conn.cursor()

    def hp(pw):
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

    # 1. Users (all passwords: admin123 for admin, pass123 for others)
    users = [
        ("admin", hp("admin123"), "admin"),
        ("frontdesk1", hp("pass123"), "front_desk"),
        ("finance1", hp("pass123"), "finance_manager"),
        ("maint1", hp("pass123"), "maintenance"),
        ("manager1", hp("pass123"), "manager"),
        ("tenant1", hp("pass123"), "tenant"),
        ("tenant2", hp("pass123"), "tenant"),
    ]
    for u in users:
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", u)

    # 2. Staff records
    for s in [(2, "EMP001", "Front Desk"), (3, "EMP002", "Finance"), (4, "EMP003", "Maintenance"), (5, "EMP004", "Management")]:
        cursor.execute("INSERT OR IGNORE INTO staff (user_id, employee_id, department) VALUES (?, ?, ?)", s)

    # 3. Apartments across 4 cities
    apts = [
        ("101", "10 Park St", "Bristol", 2, 850.00, 650, "Occupied"),
        ("102", "10 Park St", "Bristol", 1, 600.00, 450, "Vacant"),
        ("201", "25 Queen Rd", "Cardiff", 3, 1100.00, 900, "Occupied"),
        ("301", "5 King Ln", "London", 2, 1500.00, 700, "Vacant"),
        ("401", "8 High St", "Manchester", 1, 550.00, 400, "Vacant"),
    ]
    for a in apts:
        cursor.execute("INSERT OR IGNORE INTO apartments (unit_number, address, city, number_of_rooms, rental_price, square_footage, status) VALUES (?,?,?,?,?,?,?)", a)

    # 4. Tenants with full brief-required fields
    ts = [
        (6, "NI123456A", "John Smith", "07712345678", "john@email.com", "Software Engineer", "Dr. Adams", "Jane Smith", "2 bed flat", 1, "2025-01-01", "2026-01-01", 850.00, 850.00, "Active"),
        (7, "NI789012B", "Sarah Jones", "07798765432", "sarah@email.com", "Teacher", "Mr. Brown", "Tom Jones", "3 bed house", 3, "2025-06-01", "2026-06-01", 1100.00, 1100.00, "Active"),
    ]
    for t in ts:
        cursor.execute("INSERT OR IGNORE INTO tenants (user_id, ni_number, full_name, phone_number, email, occupation, references_info, emergency_contact, apartment_requirements, apartment_id, lease_start_date, lease_end_date, deposit_amount, monthly_rent, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)

    conn.commit()
    conn.close()
    print("✅ Database seeded with mock data!")
    print("   Logins: admin/admin123, frontdesk1/pass123, finance1/pass123, maint1/pass123, manager1/pass123")

if __name__ == "__main__":
    if os.path.exists("pams.db"):
        os.remove("pams.db")
        print("Old database removed.")
    seed()
