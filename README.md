# Paragon Apartment Management System (PAMS)

## Overview

This is the group portfolio project for **Advanced Software Development (UFCF8S-30-2)** at UWE Bristol.
PAMS is a role-based desktop application built with Python and CustomTkinter to manage tenants, apartments, invoices, payments, maintenance requests, and complaints for a fictional property company.

---

## Team Members

| Name | Student ID | Role |
|------|-----------|------|
| **Omar Alfrouh** | 24020879 | Group Leader, Scrum Master, Core Architecture & Reports |
| **Feras Bader** | 24033513 | Tenant Management |
| **Ahmed Deraz** | 24046227 | Payment & Billing |
| **Numair** | 24026758 | Maintenance & Testing |

---

## Setup Instructions

### Prerequisites
- Python 3.10+ (tested on 3.14)
- `pip` for package management

### 1. Clone the repository
```bash
git clone git@github.com:OmarFrouh/ASD-UWE-2026.git
cd ASD-UWE-2026
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the database and run
```bash
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py
```

---

## Test Accounts

| Username | Password | Role | Tabs visible |
|----------|----------|------|--------------|
| `admin` | `admin123` | Admin | All tabs |
| `frontdesk1` | `pass123` | Front Desk | Dashboard, Tenants |
| `finance1` | `pass123` | Finance Manager | Dashboard, Invoices, Payments |
| `maint1` | `pass123` | Maintenance | Dashboard, Maintenance |
| `manager1` | `pass123` | Manager | Dashboard, Reports |

---

## Running Automated Tests

Always run tests using the project venv, **not** the system Python:
```bash
./venv/bin/python3 -m unittest discover -s tests -v
```
Expected: **330 tests, all passing**.

---

## Project Structure

```
├── main.py                    # Entry point
├── database_manager.py        # SQLite wrapper
├── auth_manager.py            # Login & user management
├── property_manager.py        # Apartment CRUD
├── tenant_manager.py          # Tenant lifecycle, complaints
├── invoice_manager.py         # Invoice generation & overdue
├── payment_manager.py         # Payment recording & receipts
├── maintenance_manager.py     # Tickets, costs, scheduling
├── report_manager.py          # Occupancy & financial reports
├── notification_manager.py    # Overdue & lease alerts
├── seed_db.py                 # Seeds mock data for testing
├── requirements.txt           # Python dependencies
├── views/                     # All CustomTkinter UI files
└── tests/                     # All unittest test files
```

---

## Development Workflow

- **`main` branch** — verified, submission-ready code only
- **`dev` branch** — integration branch; feature PRs merge here
- **Feature branches** — `feature/<scope>` → PR → `dev` → `main`
- All PRs reviewed by Omar before merge; no direct pushes to `dev` or `main` except hotfixes

---

## Documentation

- [Backlog](BACKLOG.md)
- Sprint guides in `guides/` (gitignored — local team use only)
