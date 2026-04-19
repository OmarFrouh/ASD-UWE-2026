# Student Name: Omar Alfrouh
# Student ID: 24020879

class PropertyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_apartment(self, unit_number, address, rental_price, square_footage, city="Bristol", number_of_rooms=1):
        if not unit_number or not address:
            raise ValueError("Unit number and address are required.")
        if not rental_price or not square_footage:
            raise ValueError("Rent and size are required.")
        rental_price = float(rental_price)
        square_footage = int(square_footage)
        number_of_rooms = int(number_of_rooms)
        if rental_price <= 0:
            raise ValueError("Rent must be positive.")
        if square_footage <= 0:
            raise ValueError("Square footage must be positive.")
        if number_of_rooms <= 0:
            raise ValueError("Number of rooms must be positive.")

        query = """
            INSERT INTO apartments (unit_number, address, city, number_of_rooms, rental_price, square_footage)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db_manager.execute_query(query, (unit_number, address, city, number_of_rooms, rental_price, square_footage))
        return True

    def get_all_apartments(self):
        return self.db_manager.fetch_all("SELECT * FROM apartments")

    def get_vacant_apartments(self):
        return self.db_manager.fetch_all("SELECT * FROM apartments WHERE status='Vacant'")

    def get_cities(self):
        """Returns sorted list of all distinct cities currently in the database."""
        rows = self.db_manager.fetch_all("SELECT DISTINCT city FROM apartments ORDER BY city")
        return [row[0] for row in rows]

    def update_apartment(self, apt_id, address, city, rooms, rent, sqft):
        if not address:
            raise ValueError("Address is required.")
        rent  = float(rent)
        sqft  = int(sqft)
        rooms = int(rooms)
        if rent <= 0:
            raise ValueError("Rent must be positive.")
        if sqft <= 0:
            raise ValueError("Square footage must be positive.")
        if rooms <= 0:
            raise ValueError("Number of rooms must be positive.")
        apt = self.db_manager.fetch_one(
            "SELECT id FROM apartments WHERE id=?", (apt_id,))
        if not apt:
            raise Exception("Apartment not found.")
        self.db_manager.execute_query(
            """UPDATE apartments
               SET address=?, city=?, number_of_rooms=?, rental_price=?, square_footage=?
               WHERE id=?""",
            (address, city, rooms, rent, sqft, apt_id))

    def delete_apartment(self, apt_id):
        apt = self.db_manager.fetch_one(
            "SELECT id FROM apartments WHERE id=?", (apt_id,))
        if not apt:
            raise Exception("Apartment not found.")
        occupied = self.db_manager.fetch_one(
            "SELECT COUNT(*) FROM tenants WHERE apartment_id=? AND status='Active'",
            (apt_id,))
        if occupied and occupied[0] > 0:
            raise Exception("Cannot delete an apartment with an active tenant assigned.")
        self.db_manager.execute_query(
            "DELETE FROM apartments WHERE id=?", (apt_id,))

    def get_apartment_detail(self, apt_id):
        apt = self.db_manager.fetch_one(
            "SELECT id, unit_number, address, city, number_of_rooms, "
            "rental_price, square_footage, status FROM apartments WHERE id=?",
            (apt_id,))
        if not apt:
            raise Exception("Apartment not found.")
        tenant = self.db_manager.fetch_one("""
            SELECT full_name, email, phone_number, monthly_rent,
                   lease_start_date, lease_end_date
            FROM tenants WHERE apartment_id=? AND status='Active'
        """, (apt_id,))
        maint_count = self.db_manager.fetch_one(
            "SELECT COUNT(*) FROM maintenance_requests WHERE apartment_id=?",
            (apt_id,))
        return {
            "id":          apt[0],
            "unit_number": apt[1],
            "address":     apt[2],
            "city":        apt[3],
            "rooms":       apt[4],
            "rent":        apt[5],
            "sqft":        apt[6],
            "status":      apt[7],
            "tenant_name":       tenant[0] if tenant else None,
            "tenant_email":      tenant[1] if tenant else None,
            "tenant_phone":      tenant[2] if tenant else None,
            "tenant_rent":       tenant[3] if tenant else None,
            "tenant_lease_start": tenant[4] if tenant else None,
            "tenant_lease_end":   tenant[5] if tenant else None,
            "maintenance_count": maint_count[0] if maint_count else 0,
        }

    def update_status(self, apartment_id, status):
        valid_statuses = ["Vacant", "Occupied", "Maintenance"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        apt = self.db_manager.fetch_one("SELECT id FROM apartments WHERE id=?", (apartment_id,))
        if not apt:
            raise Exception("Apartment not found")
        self.db_manager.execute_query("UPDATE apartments SET status=? WHERE id=?", (status, apartment_id))
