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

    def update_status(self, apartment_id, status):
        valid_statuses = ["Vacant", "Occupied", "Maintenance"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        apt = self.db_manager.fetch_one("SELECT id FROM apartments WHERE id=?", (apartment_id,))
        if not apt:
            raise Exception("Apartment not found")
        self.db_manager.execute_query("UPDATE apartments SET status=? WHERE id=?", (status, apartment_id))
