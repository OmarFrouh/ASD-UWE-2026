# Student Name: Omar Alfrouh
# Student ID: 24020879

import unittest
import os
import csv
import tempfile
from views.ui_helpers import export_table_to_csv


class TestCsvExport(unittest.TestCase):
    def setUp(self):
        self.headers = ["ID", "Name", "Amount"]
        self.rows    = [(1, "Alice", 900.0), (2, "Bob", 750.0)]

    def test_file_created(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_table_to_csv(self.headers, self.rows, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)

    def test_headers_present(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False,
                                         mode="w", newline="") as f:
            path = f.name
        try:
            export_table_to_csv(self.headers, self.rows, path)
            with open(path, newline="") as f:
                reader = list(csv.reader(f))
            self.assertEqual(reader[0], self.headers)
        finally:
            os.unlink(path)

    def test_data_row_count(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False,
                                         mode="w", newline="") as f:
            path = f.name
        try:
            export_table_to_csv(self.headers, self.rows, path)
            with open(path, newline="") as f:
                reader = list(csv.reader(f))
            self.assertEqual(len(reader), 3)  # 1 header + 2 data rows
        finally:
            os.unlink(path)

    def test_empty_data_writes_headers_only(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False,
                                         mode="w", newline="") as f:
            path = f.name
        try:
            export_table_to_csv(self.headers, [], path)
            with open(path, newline="") as f:
                reader = list(csv.reader(f))
            self.assertEqual(len(reader), 1)
            self.assertEqual(reader[0], self.headers)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
