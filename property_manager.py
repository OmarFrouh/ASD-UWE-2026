from database_manager import DatabaseManager

class PropertyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_apartment(self, unit_number, address, rental_price, square_footage):
        """
        Adds a new apartment to the database.
        """
        try:
            # Validate inputs
            if not unit_number or not address:
                raise ValueError("Unit number and address are required.")
            
            try:
                rental_price = float(rental_price)
                square_footage = int(square_footage)
            except ValueError:
                raise ValueError("Price must be a number and size must be an integer.")

            query = """
                INSERT INTO apartments (unit_number, address, rental_price, square_footage)
                VALUES (?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (unit_number, address, rental_price, square_footage))
            print(f"Apartment {unit_number} added successfully.")
            return True

        except Exception as e:
            print(f"Error adding apartment: {e}")
            raise e

    def get_all_apartments(self):
        """
        Fetches all apartments.
        """
        query = "SELECT * FROM apartments"
        return self.db_manager.fetch_all(query)
