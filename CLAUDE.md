# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PAMS (Paragon Apartment Management System) is a university coursework project (ASD-UWE-2026) - a Python desktop application for managing tenants, apartments, payments, and maintenance requests. Uses CustomTkinter for GUI and SQLite for persistence.

**Methodology**: Agile/Scrum with strict Git branching (`feature/*` → `dev` → `main`).

## Team & File Ownership

Each file is strictly owned by one team member. **Do not modify files you don't own.**

| Owner | Files |
|-------|-------|
| Omar (Lead) | `main.py`, `database_manager.py`, `auth_manager.py`, `property_manager.py`, `seed_db.py`, `views/login_view.py`, `views/main_view.py`, `views/user_view.py`, `views/apartment_view.py`, `views/ui_helpers.py`, `tests/*` |
| Feras | `tenant_manager.py`, `views/tenant_view.py` |
| Ahmed | `invoice_manager.py`, `payment_manager.py`, `views/invoice_view.py`, `views/payment_view.py` |
| Numair | `maintenance_manager.py`, `views/maintenance_view.py` |

## Commands

```bash
# Run application
python3 main.py

# Reset database with test data (removes pams.db first)
python3 seed_db.py

# Run all 27 tests
python3 -m unittest discover -s tests -v

# Run single test file
python3 -m unittest tests.test_tenant_manager -v

# Run single test
python3 -m unittest tests.test_tenant_manager.TestTenantManager.test_register_and_assign_tenant -v

# Install dependencies
pip install -r requirements.txt
```

**Test Logins** (after `seed_db.py`):
- `admin/admin123` - sees all tabs
- `frontdesk1/pass123` - Dashboard, Tenants, Maintenance
- `finance1/pass123` - Dashboard, Invoices, Payments
- `maint1/pass123` - Dashboard, Maintenance
- `manager1/pass123` - Dashboard, Tenants, Reports

## Current Status (Sprint 1 Complete)

**Sprint 1 is DONE** - all features merged to `dev`, all 20 tests passing.

Completed:
- CustomTkinter migration with dark theme
- Role-based access control (admin, front_desk, finance_manager, maintenance, manager)
- Tenant lifecycle: registration, apartment assignment, early termination (5% penalty), archival
- Finance module: invoice generation, payment recording with atomic transactions, overdue tracking
- Maintenance module: ticket creation, staff assignment, status workflow, cost/time logging
- UI fixes: trackpad scrolling, sortable table columns, form alignment, confirmation dialogs
- 27-case unittest suite covering all business logic constraints

**Sprint 2 Priorities** (what's next):
1. **Reports Module** - `views/main_view.py:106` is a placeholder; needs occupancy rates and financial aggregations
2. **Notifications System** - Flag overdue invoices, push urgent maintenance alerts
3. **Merge dev → main** - Final Sprint 1 snapshot

## Architecture

```
main.py                    # Entry point, initializes managers, launches LoginView
├── database_manager.py    # SQLite wrapper with PRAGMA foreign_keys enforced
├── auth_manager.py        # Login/logout, user creation with bcrypt hashing
├── property_manager.py    # Apartment CRUD
├── tenant_manager.py      # Registration, lease assignment, termination, archival
├── maintenance_manager.py # Tickets, staff assignment, status updates, cost logging
├── invoice_manager.py     # Invoice generation, overdue tracking
├── payment_manager.py     # Payment recording with atomic transactions
└── views/                 # CustomTkinter UI
    ├── ui_helpers.py      # Scrollable Treeviews, column sorting, trackpad normalization
    └── *_view.py          # Screen-specific layouts
```

### Key Patterns

**Manager-View Separation**: Business logic in `*_manager.py`, UI in `views/*_view.py`. Views instantiate managers and call their methods.

**Atomic Transactions**: Multi-table operations (e.g., `assign_apartment`, `record_payment`) use manual `conn.commit()`/`conn.rollback()` with try/finally to ensure data integrity.

**Role-Based Sidebar**: `main_view.py:setup_sidebar()` conditionally renders navigation buttons based on `current_user[3]` (role field).

**Test Isolation**: All tests inherit from `tests/test_base.py:BaseTest` which creates a fresh `tests/test_temp.db` for each test and cleans up after.

### Database Schema (7 tables)
- `users` - id, username, password_hash, role, created_at, last_login
- `staff` - user_id (FK), employee_id, department
- `apartments` - id, unit_number, address, city, number_of_rooms, rental_price, square_footage, status
- `tenants` - user_id (FK), ni_number, full_name, lease dates, apartment_id (FK), monthly_rent, deposit, status
- `maintenance_requests` - apartment_id (FK), tenant_id (FK), staff_id (FK), description, priority, status, time_spent, cost
- `invoices` - tenant_id (FK), issue_date, due_date, total_amount, status
- `payments` - invoice_id (FK), amount, payment_date, method, transaction_ref

### Business Rules (enforced by tests)
- Early termination: 5% of monthly rent penalty
- Archiving/terminating tenant automatically vacates apartment (prevents ghost apartments)
- Cannot invoice terminated/archived tenants
- Cannot pay already-paid invoices
- Negative payments/costs blocked
- Payments auto-mark invoices "Paid" when sum >= total_amount
- Maintenance priorities: Low, Medium, High, Urgent (sorted in listings)
- Maintenance statuses: Open → Assigned → In Progress → Fixed → Closed
- Cost logging accumulates (adds to existing values, doesn't overwrite)
