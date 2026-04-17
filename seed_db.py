# Student Name: Omar Alfrouh
# Student ID: 24020879

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
        (7, "NI789012B", "Emily Carter", "07798765432", "emily@email.com", "Teacher", "Mr. Brown", "Daniel Carter", "3 bed house", 3, "2025-06-01", "2026-06-01", 1100.00, 1100.00, "Active"),
    ]
    for t in ts:
        cursor.execute("INSERT OR IGNORE INTO tenants (user_id, ni_number, full_name, phone_number, email, occupation, references_info, emergency_contact, apartment_requirements, apartment_id, lease_start_date, lease_end_date, deposit_amount, monthly_rent, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)

    # 5. Invoices (for Sprint 2 reporting & overdue testing)
    from datetime import datetime, timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    thirty_ago = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
    due_past = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    due_future = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")

    invoices = [
        (6, thirty_ago, due_past, 850.00, "Pending"),    # John — OVERDUE
        (6, today, due_future, 850.00, "Pending"),        # John — upcoming
        (7, thirty_ago, due_past, 1100.00, "Paid"),       # Emily — paid on time
        (7, today, due_future, 1100.00, "Pending"),       # Emily — upcoming
    ]
    for inv in invoices:
        cursor.execute("INSERT OR IGNORE INTO invoices (tenant_id, issue_date, due_date, total_amount, status) VALUES (?,?,?,?,?)", inv)

    # 6. Payments (partial data for financial summary)
    payments = [
        (3, 1100.00, thirty_ago, "Bank Transfer", "TXN-001"),  # Emily's paid invoice
    ]
    for pay in payments:
        cursor.execute("INSERT OR IGNORE INTO payments (invoice_id, amount, payment_date, method, transaction_ref) VALUES (?,?,?,?,?)", pay)

    # 7. Maintenance requests (for cost reporting)
    maint_requests = [
        (1, 6, 4, "Leaking kitchen tap", "High", "Fixed", thirty_ago, 2.5, 150.00),
        (3, 7, 4, "Broken window latch", "Medium", "Fixed", thirty_ago, 1.0, 75.00),
        (1, 6, None, "Flickering hallway light", "Low", "Open", today, None, None),
    ]
    for mr in maint_requests:
        cursor.execute("""INSERT OR IGNORE INTO maintenance_requests
            (apartment_id, tenant_id, staff_id, description, priority, status, date_reported, time_spent, cost)
            VALUES (?,?,?,?,?,?,?,?,?)""", mr)

    # 8. Complaints (Sprint 3 — complaint logs testing)
    complaints = [
        (6, today, "Noisy neighbors", "Loud music from adjacent unit every night after 11pm", "Open", None),
        (7, thirty_ago, "Parking issue", "Unauthorized vehicle in my reserved parking spot #7", "Resolved", today),
    ]
    for c in complaints:
        cursor.execute("""INSERT OR IGNORE INTO complaints
            (tenant_id, date_logged, subject, description, status, resolved_date)
            VALUES (?,?,?,?,?,?)""", c)

    conn.commit()
    conn.close()
    print("✅ Database seeded with mock data!")
    print("   Logins: admin/admin123, frontdesk1/pass123, finance1/pass123, maint1/pass123, manager1/pass123")

if __name__ == "__main__":
    if os.path.exists("pams.db"):
        os.remove("pams.db")
        print("Old database removed.")
    seed()
