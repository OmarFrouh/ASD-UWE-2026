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

All student ID headers fixed as of 13 Apr (Sprint 4 Step 1). All files verified clean — `grep -rn "YOUR_ID" --include="*.py" .` returns zero hits.

---

## Commands

```bash
# Run application (always use project venv)
./venv/bin/python3 main.py

# Reset database with test data
./venv/bin/python3 seed_db.py

# Run all tests (must use venv — system python3 has no bcrypt)
./venv/bin/python3 -m unittest discover -s tests -v

# Run single test file
./venv/bin/python3 -m unittest tests.test_tenant_manager -v

# Install / refresh dependencies
source venv/bin/activate && pip install -r requirements.txt
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

### Sprint 3 — COMPLETE ✅ (merged to `dev`)

All 4 members done. **189 tests total, all passing.** Guides in `guides/sprint3/`.

| Requirement | Brief Reference | Owner | Status |
|-------------|----------------|-------|--------|
| DB + Seed + Tests foundation | — | Omar | ✅ DONE |
| Update tenant info (edit records) | "adding, **updating**, and removing" | Feras | ✅ DONE — PR #26 (8 Apr) |
| 1-month notice period | "they must give 1 month notice" | Feras | ✅ DONE — PR #26 (8 Apr) |
| Complaint logs | "complaint logs" under Tenant Mgmt | Feras | ✅ DONE — PR #26 (8 Apr) |
| Billing/dues receipts | "generating the billing/dues receipts" | Ahmed | ✅ DONE — PR #27 (9 Apr) |
| Edge-case tests (16) | Element 3 foundation | Numair | ✅ DONE — PR #28 (12 Apr) |

**What's on `dev` (as of 13 Apr):**
- Complaints table, seed data, `tests/test_sprint3.py` (32 tests) — Omar
- Edit Tenant tab, Complaints tab, 1-month notice, complaint methods — Feras (PR #26)
- Billing receipt popup, `get_receipt_data()`, `record_payment()` → payment_id, 8 tests — Ahmed (PR #27)
- 16 edge-case tests covering complaint isolation, update field targeting, notice period boundaries — Numair (PR #28)

**Test count on `dev`:** 133 existing + 32 Sprint 3 + 8 Ahmed + 16 Numair = **~189 tests passing**

---

### Sprint 4 — IN PROGRESS (Apr 13–23): Final submission prep

**Goal:** Finishing Sprint 4 = submission. No new code features. See `guides/sprint4/` for full guides.

**Deadline: 23 April 2026, 14:00 UK time** (hard — no 48-hour window).

| # | Deliverable | Brief Element | Owner | Status |
|---|-------------|---------------|-------|--------|
| 1 | UML diagrams PDF (use case + class + ≥3 sequence) exported from `pmas.asta` | Element 1 (35 marks) | Omar | ⬜ TODO |
| 2 | Fix 10 `[YOUR_ID]` headers on Omar root/view files | Element 2 requirement | Omar | ✅ DONE — 13 Apr (PR #29) |
| 3 | Fix 7 missing headers on `tests/*.py` + correct Ahmed/Numair test headers | Element 2 requirement | Omar | ✅ DONE — 13 Apr (PR #29) |
| 4 | Update root `README.md` (full team, setup, test accounts) | Element 2 | Omar | ✅ DONE — 13 Apr (PR #29) |
| 5 | Write `README.txt` with run instructions + passwords | Element 2 | Omar | ✅ DONE — 16 Apr |
| 6 | Refresh `requirements.txt` from venv | Element 2 | Omar | ✅ DONE — 13 Apr (PR #29) |
| 7 | Regenerate `pams.db` via `seed_db.py` | Element 2 | Omar | ⬜ Do just before ZIP |
| 8 | Merge `feature/sprint4-submission` → `dev` → `main`, tag `submission-final` | Process | Omar | ⬜ TODO — PR #29 ready to merge |
| 9 | Build submission ZIP `Group28_<StudentID>.zip` | Process | Omar | ⬜ TODO |
| 10 | **Testing Document PDF** (test case table + screenshots) | Element 3 (10 marks) | Numair | ⬜ TODO |
| 11 | **Agile Practices Report PDF** (methodology + contributions) | Element 2 | Omar compiles + all 4 write own section | ⬜ TODO |
| 12 | Demo rehearsal with all 5 test accounts | Task 2 (25 marks) | All 4 | ⬜ TODO |
| 13 | Individual upload to Blackboard | Process | All 4 | ⬜ TODO |

**Sprint 4 guide structure (in `guides/sprint4/`):**
- `SUBMISSION_CHECKLIST.md` — master tracker
- `SPRINT4_OMAR.md` — lead guide (biggest)
- `SPRINT4_FERAS.md`, `SPRINT4_AHMED.md`, `SPRINT4_NUMAIR.md` — per-member guides
- `DIAGRAMS_REQUIREMENTS.md` — what must be in `diagrams.pdf`
- `AGILE_REPORT_OUTLINE.md` — Agile Practices PDF structure
- `TESTING_DOCUMENT_OUTLINE.md` — Numair's Testing Doc structure
- `DEMO_SCRIPT.md` — viva rehearsal script
- `GIT_WORKFLOW.md` — Sprint 4 git progress tracker
- `README_TEMPLATE.txt` — starter for `README.txt`

**Student ID header status: ✅ ALL FIXED (13 Apr, PR #29)**

All 17 files corrected. `grep -rn "YOUR_ID" --include="*.py" .` → zero hits.
Note: `tests/test_ahmed_sprint2.py` and `tests/test_numair_sprint2.py` were also corrected (had wrong Omar ID — fixed to Ahmed 24046227 and Numair 24026758 respectively).

---

## Current Dev Branch State (as of Apr 16 2026)

**Branch:** `feature/sprint4-submission` (open PR #29 → `dev`) — 2 commits ahead of dev  
**Tests:** 189 passing on `dev`  
**Sprint 4 progress:** Steps 2, 3, 4, 5, 6 done. Step 1 (diagrams) is next — `pmas.asta` ready to open in Astah.  
**Last merges:** PR #26 (Feras), PR #27 (Ahmed), PR #28 (Numair)  
**Pending PRs:** PR #29 `feature/sprint4-submission` → `dev` (ready to merge — all Sprint 4 file work done)

---

## Brief Requirements Status

| Requirement | Brief Reference | Status | Sprint | Owner |
|-------------|----------------|--------|--------|-------|
| Update tenant info (edit records) | "adding, **updating**, and removing" | ✅ Done | Sprint 3 | Feras |
| 1-month notice period on early termination | "they must give 1 month notice" | ✅ Done | Sprint 3 | Feras |
| Complaint logs | "complaint logs" under Tenant Mgmt | ✅ Done | Sprint 3 | Feras |
| Billing/dues receipts | "generating the billing/dues receipts" | ✅ Done | Sprint 3 | Ahmed |
| Sprint 3 edge-case automated tests (16) | Element 3 foundation | ✅ Done | Sprint 3 | Numair |
| Notification badge (clickable, shows details) | Sprint 2 | ✅ Done | Sprint 2 | Omar |
| Monthly revenue in Financial Summary | Sprint 2 | ✅ Done | Sprint 2 | Ahmed |
| User list in Users tab | Sprint 2 QA | ✅ Done | Sprint 2 QA | Omar |
| App resizable / fullscreen | Sprint 2 QA | ✅ Done | Sprint 2 QA | Omar |
| Scrolling on all form views | Sprint 2 QA | ✅ Done | Sprint 2 QA | Omar |
| **UML diagrams PDF** (use case + class + ≥3 sequence) | Element 1 (35 marks) | 🔜 Sprint 4 | Sprint 4 | Omar |
| **Testing Document PDF** (manual cases + screenshots + automated results) | Element 3 (10 marks) | 🔜 Sprint 4 | Sprint 4 | Numair |
| **Agile Practices Report PDF** (methodology + contributions + git evidence) | Element 2 | 🔜 Sprint 4 | Sprint 4 | Omar compiles + team writes own sections |
| Student ID headers on all `.py` files | Element 2 | ✅ Done — 13 Apr | Sprint 4 | Omar |
| `README.txt` with run instructions + test passwords | Element 2 | ✅ Done — 16 Apr | Sprint 4 | Omar |
| `requirements.txt` refreshed from `pip list` | Element 2 | ✅ Done — 13 Apr | Sprint 4 | Omar |
| Merge `dev` → `main`, tag `submission-final` | Process | 🔜 Sprint 4 | Sprint 4 | Omar |
| Submission ZIP `Group28_<StudentID>.zip` + individual Blackboard upload | Process | 🔜 Sprint 4 | Sprint 4 | All 4 |
| Demo/viva rehearsal | Task 2 (25 marks) | 🔜 Sprint 4 | Sprint 4 | All 4 |

---

## Submission Checklist (from brief.md)

- [ ] **ONE PDF** with all UML diagrams (use case + class + ≥3 sequence) — exported from `pmas.asta`
- [x] All `.py` source files with **student name + ID** at top — ✅ done 13 Apr
- [x] `requirements.txt` (bcrypt, customtkinter, darkdetect, packaging) — ✅ done 13 Apr
- [x] `README.txt` — run instructions and all test passwords — ✅ done 16 Apr
- [ ] `pams.db` — SQLite database with mock/seed data (run `seed_db.py` just before packaging)
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
├── tenant_manager.py      # Registration, lease, termination, archival, search/filter, complaints
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

### Database Schema (8 tables — Sprint 3)
- `users` — id, username, password_hash, role, created_at, last_login
- `staff` — user_id (FK), employee_id, department
- `apartments` — id, unit_number, address, city, number_of_rooms, rental_price, square_footage, status
- `tenants` — user_id (FK), ni_number, full_name, phone, email, occupation, references, emergency_contact, apartment_requirements, apartment_id (FK), lease_start, lease_end, monthly_rent, deposit, status
- `maintenance_requests` — apartment_id (FK), tenant_id (FK), staff_id (FK), description, priority, status, scheduled_date, date_reported, date_resolved, time_spent, cost
- `invoices` — tenant_id (FK), issue_date, due_date, total_amount, status
- `payments` — invoice_id (FK), amount, payment_date, method, transaction_ref
- `complaints` — id, tenant_id (FK), date_logged, subject, description, status, resolved_date *(Sprint 3)*

### Business Rules (enforced by tests)
- Early termination: 5% of monthly rent penalty + 1-month notice (effective date = today+30 days) — Sprint 3 returns dict `{"penalty", "effective_date"}`
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

## No AI Traces — Hard Rule

This is a graded university submission. **Nothing in this repo — commits, code, comments, or docs — may read as AI-generated.** Markers and tools that check for AI authorship must find nothing suspicious.

**Commit messages:** Write as a developer would. Short, plain, lowercase preferred. Describe what changed and why.
- Bad: "Meticulous sweep — fixed terminal-killing fake logout and deadly missing confirmation prompts"
- Bad: "injected natively-tracked Cost scalars into data grid for global visibility"
- Bad: "built and integrated comprehensive backend unittesting suite enforcing all business-logic constraints"
- Good: "fix logout not closing window; add missing confirmation dialogs"
- Good: "add time_spent and cost columns to maintenance tickets table"
- Good: "add 20 unit tests for tenant and finance managers"

**Code comments:** Only where logic is non-obvious. No flowery descriptions, no "This function comprehensively handles...", no AI-typical meta-commentary.

**Never reference:** Claude, AI, LLMs, Copilot, or any AI tool anywhere in commits, code, comments, or docs.

**Fixes are silent:** If correcting something AI-related (removing a trailer, rewording a message, cleaning up a comment), the commit message must describe the change naturally — never mention that an AI wrote it, that it was AI-sounding, or that you're removing AI traces. e.g. if removing a bad comment, the commit just says "clean up inline comments in tenant_manager" — not "remove AI-generated comments".

---

## Git Workflow

Branch naming: `feature/<scope>` → PR into `dev` → merge to `main` at sprint end.

Each team member works on their own branch and opens a PR for Omar to review before merging. **Do not push directly to `dev` or `main`** (except Omar for hotfixes).

Sprint 3 branch: `feature/sprint3-missing-features` for the 4 brief gap items.

The project board and GitHub Issues track sprint progress. BACKLOG.md reflects the product backlog with sprint assignments.
