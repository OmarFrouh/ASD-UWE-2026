# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

class PropertyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_apartment(self, unit_number, address, rental_price, square_footage, city="Bristol", number_of_rooms=1):
        if not unit_number or not address:
            raise ValueError("Unit number and address are required.")
        rental_price = float(rental_price)
        square_footage = int(square_footage)
        number_of_rooms = int(number_of_rooms)

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

    def update_status(self, apartment_id, status):
        self.db_manager.execute_query("UPDATE apartments SET status=? WHERE id=?", (status, apartment_id))
