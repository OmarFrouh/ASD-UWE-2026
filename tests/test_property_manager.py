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

    # ── update_apartment tests ────────────────────────────────────────────────

    def _add_and_get_id(self, unit="A101"):
        self.prop.add_apartment(unit, "Old Street", "800", "500", "Bristol", "2")
        return self.prop.get_all_apartments()[0][0]

    def test_update_apartment_success(self):
        apt_id = self._add_and_get_id()
        self.prop.update_apartment(apt_id, "New Road", "Cardiff", "3", "1200", "700")
        apt = self.prop.get_all_apartments()[0]
        self.assertEqual(apt[2], "New Road")
        self.assertEqual(apt[3], "Cardiff")
        self.assertEqual(apt[4], 3)
        self.assertAlmostEqual(apt[5], 1200.0)
        self.assertEqual(apt[6], 700)

    def test_update_apartment_nonexistent_fails(self):
        with self.assertRaises(Exception) as ctx:
            self.prop.update_apartment(9999, "Some Road", "Bristol", "2", "900", "500")
        self.assertIn("not found", str(ctx.exception))

    def test_update_apartment_empty_address_fails(self):
        apt_id = self._add_and_get_id()
        with self.assertRaises(ValueError) as ctx:
            self.prop.update_apartment(apt_id, "", "Bristol", "2", "900", "500")
        self.assertIn("Address is required", str(ctx.exception))

    def test_update_apartment_negative_rent_fails(self):
        apt_id = self._add_and_get_id()
        with self.assertRaises(ValueError) as ctx:
            self.prop.update_apartment(apt_id, "Road", "Bristol", "2", "-100", "500")
        self.assertIn("Rent must be positive", str(ctx.exception))

    def test_update_apartment_zero_sqft_fails(self):
        apt_id = self._add_and_get_id()
        with self.assertRaises(ValueError) as ctx:
            self.prop.update_apartment(apt_id, "Road", "Bristol", "2", "900", "0")
        self.assertIn("Square footage must be positive", str(ctx.exception))

    def test_update_apartment_zero_rooms_fails(self):
        apt_id = self._add_and_get_id()
        with self.assertRaises(ValueError) as ctx:
            self.prop.update_apartment(apt_id, "Road", "Bristol", "0", "900", "500")
        self.assertIn("rooms must be positive", str(ctx.exception))
