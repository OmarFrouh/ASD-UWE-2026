# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

## What This Project Is

**PAMS** (Paragon Apartment Management System) is a **UWE Bristol university group coursework** for the module *Advanced Software Development (UFCF8S-30-2)*. It is a graded Python desktop application submitted as a Portfolio (75%) + Viva/Demo (25%).

**Submission deadline: 23 April 2026 at 14:00 UK time.** This is a hard deadline — no 48-hour extension applies.

The brief is in `brief.md`. All implementation decisions must be traceable back to requirements in that document. When in doubt about whether to build a feature or how to implement it, read `brief.md` first.

The team follows **Agile/Scrum** with 4 sprints. Sprint plans, per-member task guides, and workflow instructions are in `guides/sprint1/` and `guides/sprint2/`. These are the authoritative source for what each person is supposed to build and in what order.

---

## Team, IDs & File Ownership

Every `.py` file must have the correct student name and ID at the top — this is a submission requirement from the brief.

| Member | Student ID | Owned Files |
|--------|-----------|-------------|
| Omar Al Frouh (Lead) | 24020879 | `main.py`, `database_manager.py`, `auth_manager.py`, `property_manager.py`, `seed_db.py`, `report_manager.py`, `notification_manager.py`, `views/login_view.py`, `views/main_view.py`, `views/user_view.py`, `views/apartment_view.py`, `views/ui_helpers.py`, `tests/*` |
| Feras Bader | 24033513 | `tenant_manager.py`, `views/tenant_view.py` |
| Ahmed Deraz | 24046227 | `invoice_manager.py`, `payment_manager.py`, `views/invoice_view.py`, `views/payment_view.py` |
| Numair (ID TBC) | TBC | `maintenance_manager.py`, `views/maintenance_view.py` |

**Do not modify files you don't own** unless it is a cross-cutting fix authorized by Omar (the lead).

Files currently missing their student ID header (needs fixing before submission):
- All Omar-owned files still showing `[YOUR_ID]` must be updated to `24020879`
- Numair's files once his ID is confirmed

---

## Commands

```bash
# Run application
python3 main.py

# Reset database with test data
python3 seed_db.py

# Run all tests
python3 -m unittest discover -s tests -v

# Run single test file
python3 -m unittest tests.test_tenant_manager -v

# Install dependencies
pip install -r requirements.txt
```

**Test Logins** (after `seed_db.py`):
- `admin / admin123` — all tabs
- `frontdesk1 / pass123` — Dashboard, Tenants, Maintenance
- `finance1 / pass123` — Dashboard, Invoices, Payments
- `maint1 / pass123` — Dashboard, Maintenance
- `manager1 / pass123` — Dashboard, Tenants, Reports

---

## Sprint Status

### Sprint 1 — COMPLETE (merged to dev)
- Role-based access control (5 roles: admin, front_desk, finance_manager, maintenance, manager)
- Tenant: registration, apartment assignment, early termination (5% penalty), archival
- Finance: invoice generation, payment recording, overdue tracking
- Maintenance: ticket creation, staff assignment, priority/status workflow, cost/time logging
- Security: bcrypt hashing, parameterized SQL, input validation
- 54 automated unit tests, all passing

### Sprint 2 — IN PROGRESS
**Omar (done, merged to dev):**
- `report_manager.py` — occupancy report (by city), financial summary (collected vs pending), maintenance cost report
- `notification_manager.py` — overdue invoices, expiring leases (30-day window), upcoming maintenance
- `views/report_view.py` — full Reports tab with city filters and summary cards
- Notification badge in main header

**Feras (done, merged to dev):**
- `search_tenants()` — search by name, NI, email, phone
- `filter_tenants_by_status()` — filter by Active/Archived/Terminated/All
- `get_tenant_count_by_status()` — status summary bar
- Search bar + filter dropdown + summary counts in the Active Tenants tab

**Ahmed (pending):**
- Overdue badges on invoice list
- Payment method breakdown report

**Numair (pending):**
- Communicate maintenance scheduled date to tenant (notification display)

### Sprint 3 — UPCOMING (Apr 14–18): Testing + Documentation
- Formal test case table (PDF) with pass/fail screenshots — Numair
- Agile practices report PDF — Omar
- Remaining brief gaps: tenant update, complaint logs, 1-month notice enforcement

### Sprint 4 — UPCOMING (Apr 19–22): Submission prep
- Export all UML diagrams from `pmas.asta` into one PDF
- Fix all `[YOUR_ID]` headers across every `.py` file
- Create submission ZIP per brief instructions
- Demo rehearsal

---

## Brief Requirements Status

These are the requirements from `brief.md` that still need implementation:

| Requirement | Brief Reference | Status | Sprint |
|-------------|----------------|--------|--------|
| Update tenant info (edit records) | "adding, **updating**, and removing" | ❌ Missing | Sprint 3 |
| 1-month notice period on early termination | "they must give 1 month notice" | ❌ Missing | Sprint 3 |
| Complaint logs | "complaint logs" under Tenant Mgmt | ❌ Missing | Sprint 3 |
| Billing/dues receipts | "generating the billing/dues receipts" | ❌ Missing | Sprint 3 |
| Ahmed: overdue badges on invoices | Sprint 2 backlog | ❌ Pending | Sprint 2 |
| Ahmed: payment method breakdown | Sprint 2 backlog | ❌ Pending | Sprint 2 |

---

## Submission Checklist (from brief.md)

The ZIP file must contain, per brief requirements:
- [ ] **ONE PDF** with all UML diagrams (use case + class + ≥3 sequence) — exported from `pmas.asta`
- [ ] All `.py` source files with **student name + ID** at top of each file
- [ ] `requirements.txt` (output of `pip list`)
- [ ] `README.txt` — run instructions and all test passwords
- [ ] `pams.db` — SQLite database with mock/seed data
- [ ] **Testing document PDF** — test case table (Description / Input / Actual / Expected) + automated test screenshots
- [ ] **Agile practices report PDF** — Scrum evidence, sprint reviews, Git log, contribution breakdown

Each team member uploads the full ZIP individually on Blackboard.

---

## Architecture

```
main.py                    # Entry point — initializes all managers, launches LoginView
├── database_manager.py    # SQLite wrapper, PRAGMA foreign_keys, create_tables()
├── auth_manager.py        # Login, user/staff creation, bcrypt hashing
├── property_manager.py    # Apartment CRUD, vacancy tracking
├── tenant_manager.py      # Registration, lease, termination, archival, search/filter
├── maintenance_manager.py # Tickets, staff assignment, status workflow, cost logging
├── invoice_manager.py     # Invoice generation, overdue detection
├── payment_manager.py     # Payment recording with atomic transactions
├── report_manager.py      # Occupancy, financial, maintenance cost reports
├── notification_manager.py# Overdue invoices, expiring leases, upcoming maintenance
└── views/
    ├── ui_helpers.py      # Scrollable Treeviews, column sorting, trackpad scroll
    └── *_view.py          # Screen-specific layouts (one per module)
```

### Key Patterns

**Manager-View Separation**: Business logic in `*_manager.py`, UI only in `views/*_view.py`.

**Atomic Transactions**: Multi-table writes use `conn.commit()`/`conn.rollback()` with `try/finally`.

**Role-Based Sidebar**: `main_view.py:setup_sidebar()` renders tabs based on `current_user[3]` (role).

**Test Isolation**: All tests extend `tests/test_base.py:BaseTest` — creates a fresh `tests/test_temp.db` per test, cleaned up after.

### Database Schema (7 tables)
- `users` — id, username, password_hash, role, created_at, last_login
- `staff` — user_id (FK), employee_id, department
- `apartments` — id, unit_number, address, city, number_of_rooms, rental_price, square_footage, status
- `tenants` — user_id (FK), ni_number, full_name, phone, email, occupation, references, emergency_contact, apartment_requirements, apartment_id (FK), lease dates, monthly_rent, deposit, status
- `maintenance_requests` — apartment_id (FK), tenant_id (FK), staff_id (FK), description, priority, status, scheduled_date, date_reported, date_resolved, time_spent, cost
- `invoices` — tenant_id (FK), issue_date, due_date, total_amount, status
- `payments` — invoice_id (FK), amount, payment_date, method, transaction_ref

### Business Rules (enforced by tests)
- Early termination: 5% of monthly rent penalty (1-month notice not yet enforced — Sprint 3)
- Terminating/archiving a tenant automatically vacates their apartment
- Cannot assign apartment to Terminated or Archived tenant
- Cannot invoice Terminated or Archived tenants
- Cannot pay an already-paid invoice
- Negative payments and maintenance costs are blocked
- Payments auto-mark invoices as "Paid" when cumulative sum ≥ total_amount
- Maintenance priorities: Low, Medium, High, Urgent
- Maintenance workflow: Open → Assigned → In Progress → Fixed → Closed
- Cost logging accumulates (adds to existing, does not overwrite)

---

## Git Workflow

Branch naming: `feature/<scope>` → PR into `dev` → merge to `main` at sprint end.

Each team member works on their own branch and opens a PR for Omar to review before merging. **Do not push directly to `dev` or `main`** (except Omar for hotfixes).

The project board and GitHub Issues track sprint progress. BACKLOG.md reflects the product backlog with sprint assignments.
