# CLAUDE.md

This file provides project guidelines and context for all developers working in this repository.

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
| Numair | 24026758 | `maintenance_manager.py`, `views/maintenance_view.py` |

**Do not modify files you don't own** unless it is a cross-cutting fix authorized by Omar (the lead). Omar has made cross-cutting fixes to all team member files throughout Sprint 2 — this is authorised.

Files currently missing their student ID header (needs fixing before submission):
- All Omar-owned files still showing `[YOUR_ID]` must be updated to `24020879`:
  `main.py`, `database_manager.py`, `auth_manager.py`, `property_manager.py`, `seed_db.py`,
  `views/login_view.py`, `views/main_view.py`, `views/user_view.py`, `views/apartment_view.py`, `views/ui_helpers.py`

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
- `frontdesk1 / pass123` — Dashboard, Tenants
- `finance1 / pass123` — Dashboard, Invoices, Payments
- `maint1 / pass123` — Dashboard, Maintenance
- `manager1 / pass123` — Dashboard, Reports

---

## Sprint Status

### Sprint 1 — COMPLETE ✅ (merged to main)
- Role-based access control (5 roles: admin, front_desk, finance_manager, maintenance, manager)
- Tenant: registration, apartment assignment, early termination (5% penalty), archival
- Finance: invoice generation, payment recording, overdue tracking
- Maintenance: ticket creation, staff assignment, priority/status workflow, cost/time logging
- Security: bcrypt hashing, parameterized SQL, input validation
- 93 automated unit tests

### Sprint 2 — COMPLETE ✅ (on dev, ready to merge to main)
All 4 members done. **133 automated tests, all passing.**

**Omar:**
- `report_manager.py` — occupancy report (by city), financial summary, maintenance cost report
- `notification_manager.py` — `get_overdue_invoices()`, `get_expiring_leases()`, `get_upcoming_maintenance()`, `get_notification_count()`, `get_notifications()`
- `views/report_view.py` — Reports tab with city filters and summary cards
- Notification badge (clickable CTkButton) in header → popup lists overdue invoices + expiring leases
- Sprint 2 QA pass: dark-themed treeviews, column autofit, trackpad scroll, resize support

**Feras:**
- `search_tenants()`, `filter_tenants_by_status()`, `get_tenant_count_by_status()` in `tenant_manager.py`
- Search bar + filter dropdown + summary counts in Active Tenants tab
- Archived/Terminated tab

**Ahmed:**
- `get_overdue_with_details()`, `get_invoice_aging()` in `invoice_manager.py`
- `get_collected_vs_pending()`, `get_payment_history_by_method()`, `get_monthly_revenue()` in `payment_manager.py`
- Overdue badges (`⚠️ OVERDUE`) on invoice list; Late Payment Notifications tab
- Financial Summary tab with payment method breakdown + monthly revenue chart
- 39 unit tests in `tests/test_ahmed_sprint2.py`

**Numair:**
- `get_cost_report_by_apartment()`, `get_cost_report_by_city()`, `get_tickets_by_status_count()`, `notify_tenant_scheduled_date()` in `maintenance_manager.py`
- Cost Report tab (summary cards + per-apartment + per-city tables)
- "Notify Tenant" section in Manage tab
- 40 unit tests in `tests/test_numair_sprint2.py`

**Post-Sprint-2 QA fixes by Omar (all on dev):**
- Notification badge `get_notifications()` implemented and wired (was dead code)
- City dropdown in apartment view is now dynamic (queries DB, not hardcoded)
- User list treeview added to Users tab (USR-01 — was missing entirely)
- `auth_manager.get_all_users()` added
- `property_manager.get_cities()` added
- Missing `*` markers added on required fields: Employee ID (user form), Size sqft (apartment form), Tenant ID (actions tab)
- App is now fully resizable / fullscreen capable — login was calling `resizable(False, False)` and main_view never re-enabled it; fixed with `resizable(True, True)` + `minsize(900, 580)` + centered on screen
- Outer `CTkScrollableFrame` added to: `user_view`, `apartment_view`, `tenant_view` (Register + Assign tabs), `maintenance_view` (Manage tab)
- `enable_trackpad_scroll` fixed to skip `ttk.Treeview` nodes (was overriding treeview's own scroll handler)
- `invoice_manager` error message improved: "No monthly rent set" instead of cryptic "Invalid amount"
- Sprint 2 test plan: `guides/sprint2/TEST_PLAN_SPRINT2.md` (~80 manual tests, 11 sections)

### Sprint 3 — UPCOMING (Apr 14–18): Missing features + Testing docs

**Missing brief requirements to implement (Omar owns all of these):**

| Requirement | Brief Reference | Owner | Notes |
|-------------|----------------|-------|-------|
| Update tenant info (edit records) | "adding, **updating**, and removing" | Omar | Add Edit button in Active Tenants tab; pre-fill form; call `update_tenant()` in tenant_manager |
| 1-month notice period on early termination | "they must give 1 month notice" | Omar | In `tenant_manager.early_termination()`: check if today < lease_start + 1 month; block or warn |
| Complaint logs | "complaint logs" under Tenant Mgmt | Omar | New table `complaints` in DB; new tab in tenant_view; log/view complaints per tenant |
| Billing/dues receipts | "generating the billing/dues receipts" | Omar | After payment recorded, show/print a formatted receipt popup with invoice + payment details |

**Documentation tasks:**
- Formal test case table PDF (Description / Input / Expected / Actual / Pass/Fail + screenshots) — **Numair**
- Agile practices report PDF (Scrum evidence, sprint reviews, Git log, contribution breakdown) — **Omar**

**Sprint 3 approach for code features:**
1. All 4 missing features are in Omar's files (`tenant_manager.py`, `views/tenant_view.py`, `payment_manager.py`/`views/payment_view.py`)
2. Add DB migration for `complaints` table in `database_manager.py` (`create_tables()` — use `IF NOT EXISTS`)
3. Write unit tests for all new manager methods before/alongside implementation
4. Keep UI changes minimal and consistent with existing patterns

### Sprint 4 — UPCOMING (Apr 19–22): Submission prep
- Merge dev → main
- Export all UML diagrams from `pmas.asta` into one PDF
- Fix all remaining `[YOUR_ID]` headers in Omar's 10 files → `24020879`
- Create submission ZIP per brief instructions
- Demo rehearsal with all 5 test accounts

---

## Current Dev Branch State (as of Apr 6 2026)

**Branch:** `dev` — clean, all tests passing  
**Tests:** 133/133 passing  
**Last commit:** `05edf63` — Fix (Omar): clearer error when generating invoice with no monthly rent

Recent commits on dev (newest first):
```
05edf63  Fix (Omar): clearer error when generating invoice with no monthly rent
567baf7  Fix (Omar): add outer scrolling to all form-heavy views
f393c9b  Fix (Omar): make app fully resizable with proper window sizing
52fbf4d  Fix (Omar): missing * markers on required form fields system-wide
6fc2c4c  Fix (Omar): USR-01 — add user list treeview to Users tab
2fd9c54  Fix (Omar): dynamic city dropdown in apartment view
7349ede  Fix (Omar): NOTIF-02 — wire notification badge popup to get_notifications()
```

---

## Brief Requirements Status

| Requirement | Brief Reference | Status | Sprint |
|-------------|----------------|--------|--------|
| Update tenant info (edit records) | "adding, **updating**, and removing" | ❌ Missing | Sprint 3 |
| 1-month notice period on early termination | "they must give 1 month notice" | ❌ Missing | Sprint 3 |
| Complaint logs | "complaint logs" under Tenant Mgmt | ❌ Missing | Sprint 3 |
| Billing/dues receipts | "generating the billing/dues receipts" | ❌ Missing | Sprint 3 |
| Notification badge (clickable, shows details) | Sprint 2 | ✅ Done | Sprint 2 |
| Monthly revenue in Financial Summary | Sprint 2 | ✅ Done | Sprint 2 |
| User list in Users tab | Sprint 2 QA | ✅ Done | Sprint 2 QA |
| App resizable / fullscreen | Sprint 2 QA | ✅ Done | Sprint 2 QA |
| Scrolling on all form views | Sprint 2 QA | ✅ Done | Sprint 2 QA |

---

## Submission Checklist (from brief.md)

- [ ] **ONE PDF** with all UML diagrams (use case + class + ≥3 sequence) — exported from `pmas.asta`
- [ ] All `.py` source files with **student name + ID** at top of each file ← 10 Omar files still need `24020879`
- [ ] `requirements.txt` (output of `pip list`)
- [ ] `README.txt` — run instructions and all test passwords
- [ ] `pams.db` — SQLite database with mock/seed data (run `seed_db.py` before packaging)
- [ ] **Testing document PDF** — test case table (Description / Input / Actual / Expected) + automated test screenshots
- [ ] **Agile practices report PDF** — Scrum evidence, sprint reviews, Git log, contribution breakdown

Each team member uploads the full ZIP individually on Blackboard.

---

## Architecture

```
main.py                    # Entry point — initializes all managers, launches LoginView
├── database_manager.py    # SQLite wrapper, PRAGMA foreign_keys, create_tables()
├── auth_manager.py        # Login, user/staff creation, bcrypt hashing, get_all_users()
├── property_manager.py    # Apartment CRUD, vacancy tracking, get_cities()
├── tenant_manager.py      # Registration, lease, termination, archival, search/filter
├── maintenance_manager.py # Tickets, staff assignment, status workflow, cost logging
├── invoice_manager.py     # Invoice generation, overdue detection
├── payment_manager.py     # Payment recording with atomic transactions
├── report_manager.py      # Occupancy, financial, maintenance cost reports
├── notification_manager.py# Overdue invoices, expiring leases, get_notifications()
└── views/
    ├── ui_helpers.py      # Dark Treeviews, column autofit+redistribute, trackpad scroll,
    │                      # enable_trackpad_scroll (skips ttk.Treeview nodes)
    └── *_view.py          # Screen-specific layouts (one per module)
```

### Key Patterns

**Manager-View Separation**: Business logic in `*_manager.py`, UI only in `views/*_view.py`.

**Atomic Transactions**: Multi-table writes use `conn.commit()`/`conn.rollback()` with `try/finally`.

**Role-Based Sidebar**: `main_view.py:setup_sidebar()` renders tabs based on `current_user[3]` (role).

**Test Isolation**: All tests extend `tests/test_base.py:BaseTest` — creates a fresh `tests/test_temp.db` per test, cleaned up after.

**Scrollable Views**: Non-tab views (`user_view`, `apartment_view`) and heavy form tabs (tenant Register/Assign, maintenance Manage) use `CTkScrollableFrame` as outer container + `enable_trackpad_scroll(scroll)` called via `.after(200, ...)`.

**Treeview Column Resize**: `setup_treeview_scroll()` in `ui_helpers.py` sets `stretch=True` on all columns + binds `<Configure>` on the container to `redistribute_columns()`. Call `autofit_columns()` after inserting data to update minimum widths.

**City Dropdown**: Apartment form city dropdown is dynamic — queries `property_manager.get_cities()` merged with 4 defaults. Any new city typed into the form appears in future dropdowns.

### Database Schema (7 tables)
- `users` — id, username, password_hash, role, created_at, last_login
- `staff` — user_id (FK), employee_id, department
- `apartments` — id, unit_number, address, city, number_of_rooms, rental_price, square_footage, status
- `tenants` — user_id (FK), ni_number, full_name, phone, email, occupation, references, emergency_contact, apartment_requirements, apartment_id (FK), lease_start, lease_end, monthly_rent, deposit, status
- `maintenance_requests` — apartment_id (FK), tenant_id (FK), staff_id (FK), description, priority, status, scheduled_date, date_reported, date_resolved, time_spent, cost
- `invoices` — tenant_id (FK), issue_date, due_date, total_amount, status
- `payments` — invoice_id (FK), amount, payment_date, method, transaction_ref

**Sprint 3 will add:**
- `complaints` — id, tenant_id (FK), date_logged, subject, description, status, resolved_date

### Business Rules (enforced by tests)
- Early termination: 5% of monthly rent penalty (1-month notice enforcement — Sprint 3)
- Terminating/archiving a tenant automatically vacates their apartment
- Cannot assign apartment to Terminated or Archived tenant
- Cannot invoice Terminated or Archived tenants
- Cannot invoice a tenant with no monthly rent and no custom amount provided
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

Sprint 3 branch: `feature/sprint3-missing-features` for the 4 brief gap items.

The project board and GitHub Issues track sprint progress. BACKLOG.md reflects the product backlog with sprint assignments.
