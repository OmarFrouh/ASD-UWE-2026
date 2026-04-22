# Team Roles & Responsibilities Matrix

**Purpose**: This document tracks who is "Captain" of which section.
**Rule**: The "Owner" has the final say on the code in their section.
**Deadline**: 23 April 2026, 14:00

---

## 1. Omar Alfrouh (Group Leader) — Student ID 24020879
*   **Role**: Scrum Master & Core Architect
*   **Responsibility**:
    *   **The Backbone**: Database, authentication, main window, and project infrastructure.
    *   **Code Review**: Merging everyone's Pull Requests.
    *   **System Design**: Owning the Class Diagram + Sequence Diagrams.
    *   **Documentation**: Agile Practices Report.
*   **Completed Tasks (Sprint 0)**:
    *   [x] Create Project Repo & Git Rules
    *   [x] Design Class Diagram (Astah) — Verified 100%
    *   [x] Design 3 Sequence Diagrams (Astah) — Verified 100%
    *   [x] Implement `DatabaseManager` (SQLite schema)
    *   [x] Implement `AuthManager` (Login, Create User, bcrypt)
    *   [x] Build `MainView` (Shell, Sidebar, Role Permissions)
    *   [x] Implement `PropertyManager` (Add/List Apartments)
    *   [x] Build `LoginView`, `UserView`, `ApartmentView`
*   **Sprint 1 Tasks (Mar 31 – Apr 6)**:
    *   [x] Reports foundation — early `report_manager.py` scaffolding
    *   [x] Seed script (`seed_db.py`) with mock tenants, apartments, invoices and tickets
    *   [x] Code review / merge all Sprint 1 PRs
*   **Sprint 2 Tasks (Apr 7 – Apr 13)**:
    *   [x] `report_manager.py` — occupancy by city, financial summary, maintenance cost report
    *   [x] `notification_manager.py` — overdue invoices, expiring leases, upcoming maintenance
    *   [x] `views/report_view.py` — Reports tab with city filter and summary cards
    *   [x] Notification badge in main header → popup listing overdue invoices and expiring leases
    *   [x] Sprint 2 QA sweep: dynamic city dropdown, user list treeview, required-field markers, app resizing, scrollable forms
*   **Sprint 3 Tasks (Apr 14 – Apr 18)**:
    *   [x] `complaints` table added to schema + seed data
    *   [x] `tests/test_sprint3.py` — 32 tests covering update tenant / notice period / complaints / receipts
*   **Sprint 4 Tasks (Apr 13 – Apr 23)**:
    *   [x] Fix 17 student-ID headers across root, `views/` and `tests/`
    *   [x] `README.md` + `README.txt` refresh (test accounts, 330-test expectation)
    *   [x] `requirements.txt` refreshed from `pip freeze`, `fpdf2` added
    *   [x] `views/theme.py` — design-token module (colors, fonts, spacing, radii)
    *   [x] UI redesign: sidebar highlight, toast + confirm dialog, dashboard KPIs, status pills, empty states, notification dropdown, keyboard shortcuts
    *   [x] `views/pdf_generator.py` — fpdf2 invoice PDF
    *   [x] `database_manager._apply_migrations()` — idempotent migration dropping legacy `UNIQUE` constraint on `tenants.apartment_id`
    *   [x] Tenant role blocked at `login_view` (staff-only system)
    *   [x] CSV export helpers on reports
    *   [x] 9 new test files added (coverage gaps, v2 managers, PDF, search, CSV, reactivate) — total 330 passing
    *   [x] Use Case + Class + 4 Sequence diagrams exported to `diagrams.pdf` (23 pages, A3)
    *   [x] Merge `dev` → `main`, tag `submission-final`
    *   [x] Agile Practices Report PDF (compile team sections)
    *   [x] Build final submission ZIP (`Group28_24020879.zip`)

---

## 2. Feras Bader (Frontend Lead) — Student ID 24033513
*   **Role**: Frontend Lead & Tenant Module Owner
*   **Responsibility**:
    *   **UI Consistency**: Making sure all tenant forms look the same.
    *   **Tenant Operations**: Everything related to tenants and leases.
    *   **Use Case Diagram**: Designing the system use case diagram (moved to Omar for Sprint 4 final export).
    *   **Testing Document**: Creating the Element 3 testing document with evidence (reassigned from Numair during Sprint 4).
*   **Sprint 1 Tasks (Mar 31 – Apr 6)** — ✅ delivered:
    *   [x] `tenant_manager.py` — registration, apartment assignment, early termination (5% penalty), archival
    *   [x] `views/tenant_view.py` — Register / Assign / Actions / Active Tenants tabs
    *   [x] 5% early-termination penalty calculation
    *   [x] Contributed to the Use Case Diagram (finalised in Sprint 4 by Omar for the exported PDF)
*   **Sprint 2 Tasks (Apr 7 – Apr 13)** — ✅ delivered:
    *   [x] `search_tenants()`, `filter_tenants_by_status()`, `get_tenant_count_by_status()`
    *   [x] Search bar + filter dropdown + summary counts in Active Tenants tab
    *   [x] Archived / Terminated tab
*   **Sprint 3 Tasks (Apr 14 – Apr 18)** — ✅ delivered in PR #26:
    *   [x] `get_tenant_by_id()`, `update_tenant()` for editing existing records
    *   [x] Modified `early_termination()` to return a dict with penalty + 30-day effective date
    *   [x] Complaint system: `log_complaint`, `get_all_complaints`, `get_complaints_for_tenant`, `resolve_complaint`
    *   [x] New Edit Tenant and Complaints tabs in `TenantView`
*   **Sprint 4 Tasks (Apr 13 – Apr 23)**:
    *   [x] Reactivate-archived-tenant support in the Register flow
    *   [x] Tenant module smoke-tested on the new redesigned UI
    *   [x] **Testing Document PDF** — manual test-case table + 330-test automated results screenshot
    *   [x] Agile Practices Report — individual contribution section
    *   [x] Demo rehearsal for tenant module (3–4 min)
    *   [x] Upload final submission ZIP to Blackboard

---

## 3. Ahmed Deraz (Finance Lead) — Student ID 24046227
*   **Role**: Finance Lead
*   **Responsibility**:
    *   **Money**: Invoices, Payments, and Financial Reports.
    *   **Privacy**: Ensuring only Finance Manager / Admin sees financial data.
*   **Sprint 1 Tasks (Mar 31 – Apr 6)** — ✅ delivered:
    *   [x] `invoice_manager.py` — monthly rent invoicing, overdue detection
    *   [x] `views/invoice_view.py` — generate invoice + all-invoice list
    *   [x] `payment_manager.py` — payment recording with atomic transactions
    *   [x] `views/payment_view.py` — payment form + history
*   **Sprint 2 Tasks (Apr 7 – Apr 13)** — ✅ delivered:
    *   [x] `get_overdue_with_details()`, `get_invoice_aging()`
    *   [x] `get_collected_vs_pending()`, `get_payment_history_by_method()`, `get_monthly_revenue()`
    *   [x] Overdue badges on invoice list + Late Payment Notifications tab
    *   [x] Financial Summary tab (method breakdown + monthly revenue)
    *   [x] 39 unit tests in `tests/test_ahmed_sprint2.py`
*   **Sprint 3 Tasks (Apr 14 – Apr 18)** — ✅ delivered in PR #27:
    *   [x] Billing receipt popup with tenant / invoice / payment details
    *   [x] `get_receipt_data()` on `PaymentManager`
    *   [x] `record_payment()` now returns `payment_id` so the receipt can be rendered immediately
    *   [x] 8 unit tests in `tests/test_ahmed_sprint3.py`
*   **Sprint 4 Tasks (Apr 13 – Apr 23)**:
    *   [x] Finance module smoke-tested against the redesigned receipt modal
    *   [x] Invoice search (`search_invoices`) + aging dashboard support
    *   [x] Agile Practices Report — individual contribution section
    *   [x] Demo rehearsal for invoices + payments (3 min)
    *   [x] Upload final submission ZIP to Blackboard

---

## 4. Numair (Maintenance Lead) — Student ID 24026758
*   **Role**: Maintenance Lead
*   **Responsibility**:
    *   **Maintenance**: The full ticketing lifecycle (report → assign → resolve → log costs).
    *   **Edge-Case Testing**: Writing targeted edge-case tests for critical flows.
*   **Sprint 1 Tasks (Mar 31 – Apr 6)** — ✅ delivered:
    *   [x] `maintenance_manager.py` — ticket CRUD, staff assignment, priority workflow, cost / time logging
    *   [x] `views/maintenance_view.py` — Create / Assign / Manage tabs
*   **Sprint 2 Tasks (Apr 7 – Apr 13)** — ✅ delivered:
    *   [x] `get_cost_report_by_apartment()`, `get_cost_report_by_city()`, `get_tickets_by_status_count()`
    *   [x] `notify_tenant_scheduled_date()`
    *   [x] Cost Report tab (summary cards + per-apartment + per-city tables)
    *   [x] "Notify Tenant" section on Manage tab
    *   [x] 40 unit tests in `tests/test_numair_sprint2.py`
*   **Sprint 3 Tasks (Apr 14 – Apr 18)** — ✅ delivered in PR #28:
    *   [x] 16 edge-case tests in `tests/test_numair_sprint3.py`
    *   [x] Complaint isolation between tenants
    *   [x] Update-tenant field targeting
    *   [x] 1-month notice-period boundaries
*   **Sprint 4 Tasks (Apr 13 – Apr 23)**:
    *   [x] Maintenance module smoke-tested against redesigned UI (priority pills, KPI cost-report cards)
    *   [x] Agile Practices Report — individual contribution section
    *   [x] Demo rehearsal for maintenance module (3 min)
    *   [x] Upload final submission ZIP to Blackboard
