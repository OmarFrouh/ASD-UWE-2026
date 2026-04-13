# Student Name: Omar Alfrouh
# Student ID: 24020879
import unittest
from tests.test_base import BaseTest
from property_manager import PropertyManager

class TestPropertyManager(BaseTest):
    def setUp(self):
        super().setUp()
        self.prop = PropertyManager(self.db)

    def test_add_valid_apartment(self):
        res = self.prop.add_apartment("A101", "123 Bristol Way", "1200", "800")
        self.assertTrue(res)
        
        apts = self.prop.get_all_apartments()
        self.assertEqual(len(apts), 1)
        self.assertEqual(apts[0][1], "A101")
        self.assertEqual(apts[0][7], "Vacant")

    def test_negative_rental_price_fails(self):
        # Negative rent should throw ValueError
        with self.assertRaises(ValueError) as context:
            self.prop.add_apartment("A102", "Address", "-500", "800")
        self.assertIn("Rent must be positive", str(context.exception))

    def test_empty_coercion_fails(self):
        # Testing the python float('') bug that we fixed
        with self.assertRaises(ValueError):
            self.prop.add_apartment("A103", "Address", "", "500")

    def test_update_status(self):
        self.prop.add_apartment("B200", "Road", "900", "400")
        apts = self.prop.get_all_apartments()
        apt_id = apts[0][0]
        
        self.prop.update_status(apt_id, "Occupied")
        
        updated = self.prop.get_all_apartments()
        self.assertEqual(updated[0][7], "Occupied")
