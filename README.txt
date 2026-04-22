============================================================
 PAMS — Paragon Apartment Management System
 Group 28 — UWE Bristol — UFCF8S-30-2
============================================================

TEAM
----
Omar Alfrouh    (24020879) — Group Leader / Architecture / Reports / Notifications
Feras Bader     (24033513) — Tenant Management
Ahmed Deraz     (24046227) — Payment & Billing
Numair          (24026758) — Maintenance / Testing

REQUIREMENTS
------------
Python 3.10 or higher, pip, and the packages in requirements.txt:
    bcrypt
    customtkinter
    darkdetect
    packaging
    fpdf2

Note for Linux users: tkinter is not bundled with Python on some distributions.
If you see "No module named tkinter", install it first:
    sudo apt install python3-tk      # Debian / Ubuntu
    sudo dnf install python3-tkinter # Fedora

SETUP
-----
1. Unzip the source_code archive and cd into the source_code folder:
       unzip source_code.zip
       cd source_code

2. Create a virtual environment and activate it:
       python3 -m venv venv
       source venv/bin/activate        # macOS / Linux
       venv\Scripts\activate           # Windows

   All subsequent commands assume the virtual environment is active.

3. Install dependencies:
       pip install -r requirements.txt

4. Database:
   A seeded database file (pams.db) is already included in this folder.
   To start fresh with new mock data, run:
       python3 seed_db.py
   This overwrites pams.db with clean seed data.

RUNNING THE APPLICATION
-----------------------
From the source_code folder:
    python3 main.py

A desktop window titled "PAMS" will open on the login screen.

TEST ACCOUNTS
-------------
After running seed_db.py you can log in with any of the following:

    Role                | Username    | Password
    --------------------+-------------+----------
    Administrator       | admin       | admin123
    Front-desk Staff    | frontdesk1  | pass123
    Finance Manager     | finance1    | pass123
    Maintenance Staff   | maint1      | pass123
    Manager             | manager1    | pass123

Each role sees a different sidebar — see the Agile Practices Report
for the full role and permissions matrix.

RUNNING THE AUTOMATED TESTS
----------------------------
Make sure the virtual environment is active, then from the source_code folder:
    python3 -m unittest discover -s tests -v

Expected result: 330 tests pass, with an OK line at the bottom.
Each test creates and tears down its own temporary SQLite database,
so tests do not affect your pams.db file.

FOLDER STRUCTURE
----------------
source_code/
    main.py                     entry point
    database_manager.py         SQLite wrapper and schema
    auth_manager.py             login, user creation, bcrypt hashing
    property_manager.py         apartment CRUD
    tenant_manager.py           tenants, complaints, early termination
    invoice_manager.py          invoice generation, overdue detection
    payment_manager.py          payments, atomic transactions, receipts
    maintenance_manager.py      tickets, staff assignment, cost logging
    report_manager.py           occupancy, financial, maintenance cost
    notification_manager.py     overdue and expiring lease notifications
    seed_db.py                  resets and populates pams.db
    pams.db                     SQLite database with seed data
    requirements.txt            pip dependencies
    README.txt                  this file
    tests/                      unittest test files (330 tests)
    views/                      CustomTkinter UI layer

SUBMISSION CONTENTS
-------------------
The full submission ZIP (Group28_<StudentID>.zip) contains:
    diagrams.pdf                  Element 1 — UML use case, class, sequence
    agile_practices_report.pdf    Element 2 — methodology and contributions
    testing_document.pdf          Element 3 — test cases and screenshots
    source_code.zip               Element 2 — this folder
    README.txt                    this file

NOTES
-----
- Desktop application only. No web component.
- All passwords are stored as bcrypt hashes. All SQL is parameterised.
- Tested on macOS and Windows with Python 3.10 and 3.12.

============================================================
