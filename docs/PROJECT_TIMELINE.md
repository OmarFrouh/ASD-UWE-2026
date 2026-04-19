# 4-Sprint Master Plan
**Deadline**: 23 April 2026, 14:00 UK
**Plan written**: 30 March 2026
**Team**: Omar (Leader), Feras Bader, Ahmed Deraz, Numair

> Live status is tracked in `docs/BACKLOG.md`. This file is the original plan with per-sprint delivery notes added at the end of each sprint.

---

## What's Already Done (Sprint 0 - Omar)

| Item | Status |
|------|--------|
| DatabaseManager (SQLite) | ✅ |
| AuthManager (Login, Create User, bcrypt) | ✅ |
| PropertyManager (Add/List Apartments) | ✅ |
| MainView (Shell, Sidebar, Role Permissions) | ✅ |
| LoginView, UserView, ApartmentView | ✅ |
| Class Diagram (Astah, verified 100%) | ✅ |
| 3 Sequence Diagrams (Login, Create Staff, Add Apartment) | ✅ |
| DB Schema (users, staff, apartments, tenants, maintenance_requests, invoices, payments) | ✅ |

---

## Full Requirements from Brief (Gap Analysis)

### ❌ NOT YET BUILT (as of plan date, 30 Mar)

| # | Requirement (from brief.md) | Brief Section | Assigned | Delivered |
|---|---------------------------|---------------|----------|-----------|
| 1 | **Register Tenant** (NI, name, phone, email, occupation, references, apt requirements, lease period) | Account/User Mgmt | Feras | ✅ Sprint 1 |
| 2 | **Tenant List** (search, filter, update, remove) | Tenant Mgmt | Feras | ✅ Sprint 1 (list) + Sprint 2 (search/filter) + Sprint 3 (update) |
| 3 | **Lease Manager** (start/end dates, renew, cancel) | Tenant Mgmt | Feras | ✅ Sprint 1 (folded into `tenant_manager.py`, no separate `lease_manager`) |
| 4 | **Early Termination** (1 month notice + 5% penalty) | Tenant Mgmt | Feras | ✅ Sprint 1 (penalty) + Sprint 3 (notice period) |
| 5 | **Archive Tenant** (moved out → inactive) | Tenant Mgmt | Feras | ✅ Sprint 1 (+ Sprint 4 reactivate flow) |
| 6 | **Assign Tenant to Apartment** (link + track occupancy) | Apartment Mgmt | Feras | ✅ Sprint 1 |
| 7 | **Invoice Generator** (PDF/text bill for monthly rent) | Payment & Billing | Ahmed | ✅ Sprint 1 (text) + Sprint 4 (PDF via fpdf2) |
| 8 | **Payment Processing** (record payments, emulate process) | Payment & Billing | Ahmed | ✅ Sprint 1 |
| 9 | **Late Payment Tracker** (flag overdue + notification) | Payment & Billing | Ahmed | ✅ Sprint 2 |
| 10 | **Financial Reports** (collected vs pending rents) | Reporting | Ahmed | ✅ Sprint 2 |
| 11 | **Maintenance Ticket** (report issue, prioritise, assign) | Maintenance | Numair | ✅ Sprint 1 |
| 12 | **Staff Assignment** (check availability, assign worker) | Maintenance | Numair | ✅ Sprint 1 |
| 13 | **Maintenance Cost Logger** (time + costs per issue) | Maintenance | Numair | ✅ Sprint 1 |
| 14 | **Communicate Dates** (notify tenant of maintenance date) | Maintenance | Numair | ✅ Sprint 2 |
| 15 | **Occupancy Report** (chart by apartment/city) | Reporting | Omar | ✅ Sprint 2 (owned by Omar in the end, not Numair) |
| 16 | **Maintenance Cost Report** (budget tracking) | Reporting | Numair | ✅ Sprint 2 |
| 17 | **Use Case Diagram** | Element 1 | Feras → Omar | ✅ Sprint 4 (finalised + exported by Omar) |
| 18 | **Testing Document** | Element 3 | Numair → Feras | 🔜 Sprint 4 (reassigned to Feras mid-Sprint 4) |
| 19 | **Agile Practices Report** | Element 2 | Omar | 🔜 Sprint 4 (compiling team sections) |
| 20 | **Mock Data** (seed DB for demo) | Element 2 | Omar | ✅ Sprint 1 + Sprint 3 (complaint data) |
| 21 | **Non-functional: Security** (bcrypt ✅, role-based ✅, input validation) | Element 2 | All | ✅ Ongoing (all sprints) |
| 22 | **Complaint Logs** (added after closer read of brief) | Tenant Mgmt | Feras | ✅ Sprint 3 |
| 23 | **Billing/Dues Receipts** (added after closer read of brief) | Payment & Billing | Ahmed | ✅ Sprint 3 |

---

## 4-Sprint Plan

### Sprint 1: Mar 31 - Apr 6 (Meeting 1)
**Focus**: Tenant Management + Use Case Diagram

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **Feras** | Build `TenantRegistrationView` (NI, name, phone, email, occupation, references, apt requirements) | Working tenant registration form |
| **Feras** | Build `TenantManager` backend (add, update, remove, archive tenant) | `tenant_manager.py` |
| **Feras** | Build `LeaseManager` (start/end, renew, early termination with 5% penalty) | `lease_manager.py` |
| **Feras** | Draw **Use Case Diagram** in Astah | Exported to PDF |
| **Ahmed** | Build `InvoiceGenerator` (create monthly rent bill, PDF/text) | `invoice_manager.py` |
| **Ahmed** | Build `PaymentProcessing` (record payments against invoices) | `payment_manager.py` |
| **Numair** | Build `MaintenanceTicketView` (report issue form, priority, status) | `maintenance_manager.py` + view |
| **Numair** | Build `StaffAssignment` (assign worker, check availability) | Part of maintenance_manager |
| **Omar** | Code review all PRs, help unblock team, prepare mock data | Seed script updated |

**Sprint 1 retrospective (Apr 6)** — all modules landed on time. `lease_manager.py` was folded into `tenant_manager.py` rather than kept separate; the lease lifecycle is small enough that splitting it added no value. 93 automated tests passing at sprint close.

---

### Sprint 2: Apr 7 - Apr 13 (Meeting 2)
**Focus**: Finance + Reports + Remaining Features

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **Feras** | Build `TenantListView` (search/filter tenants) | Working list view |
| **Feras** | Build `AssignTenantToApartment` (link tenant → apartment, update status) | Assign form + status update |
| **Ahmed** | Build `LatePaymentTracker` (flag overdue, generate notification) | Late payment alerts |
| **Ahmed** | Build `FinancialReportView` (collected vs pending rents chart) | Report dashboard |
| **Numair** | Build `MaintenanceCostLogger` (log time + costs per issue) | Cost fields in ticket |
| **Numair** | Build `OccupancyReportView` (chart: occupied vs empty by location) | Chart/dashboard |
| **Numair** | Build `MaintenanceCostReport` (budget tracking view) | Report view |
| **Omar** | Integration: wire all new views into `MainView` sidebar | All features accessible |

**Sprint 2 retrospective (Apr 13)** — scope adjusted mid-sprint: Omar took over the occupancy report so Numair could focus on the maintenance cost report; both shipped. Notification badge in the header was added as a Sprint 2 QA fix after the stand-up flagged the feature as discoverable only from the Reports tab. 133 automated tests passing at sprint close.

---

### Sprint 3: Apr 14 - Apr 18 (Meeting 3)
**Focus**: Missing Brief Requirements + Testing + Documentation + Polish

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **Feras** | Polish UI consistency across all forms | Clean UI |
| **Feras** | Edit-tenant flow (brief requirement — "updating" records) | `update_tenant()` + Edit Tenant tab |
| **Feras** | 1-month notice period on early termination (brief requirement) | `early_termination()` returns dict |
| **Feras** | Complaint logs (brief requirement) | `complaints` table + Complaints tab |
| **Ahmed** | Billing / dues receipts (brief requirement) | Receipt popup + `get_receipt_data()` |
| **Ahmed** | Input validation on all finance forms | Robust forms |
| **Numair** | Edge-case testing across brief-driven flows | 16 tests in `test_numair_sprint3.py` |
| **Omar** | Add `complaints` table + seed data + `test_sprint3.py` (32 tests) | Sprint 3 infrastructure |
| **All** | Merge all branches, resolve conflicts | Clean `dev` |

**Sprint 3 retrospective (Apr 18)** — closer re-read of the brief during Sprint 2 planning surfaced four gaps that were not in the original Sprint 0 plan: update-tenant, 1-month notice, complaint logs, and receipts. All four shipped under PRs #26 and #27. Numair authored the Sprint 3 edge-case tests in PR #28. 189 automated tests passing at sprint close.

---

### Sprint 4: Apr 13 - Apr 23 (overlapping window)
**Focus**: Submission Prep + UI Redesign + Demo Rehearsal

Original plan:

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **All** | Demo rehearsal (each member explains their part) | Practice run |
| **Omar** | Export diagrams to ONE PDF (Use Case + Class + Sequence) | `diagrams.pdf` |
| **Omar** | Add student IDs + names to all `.py` files (brief requirement) | Header comments |
| **Omar** | Create final ZIP: `Group28_StudentID.zip` | Submission package |
| **Omar** | Include `requirements.txt` (`pip list`) and `README` with run instructions | Setup docs |
| **All** | Each member uploads the ZIP individually on Blackboard | ✅ Submitted |
| **Apr 23** | **DEADLINE 14:00** | 🚨 |

**Scope expansion (Apr 13 planning meeting)** — after Sprint 3 closed with the brief-driven features in and the test suite green, we voted to spend the spare Sprint 4 capacity on a UI redesign rather than on speculative features. This produced:
*   `views/theme.py` — design-token module so colors/fonts/spacing live in one place
*   Sidebar active-state, header with dynamic page title, bell dropdown (replacing modal popup)
*   Toast + custom confirm dialog replacing every `messagebox.*` call
*   Dashboard with KPI tiles + recent activity
*   Status / priority pills on treeviews
*   Global keyboard shortcuts (`Ctrl+R`, `Ctrl+F`, `Ctrl+L`, `F11`, `Alt+1..7`, `Escape`)
*   `views/pdf_generator.py` — fpdf2 PDF invoice/receipt (brief mentions "PDF/text bill")
*   `database_manager._apply_migrations()` — legacy `UNIQUE` constraint on `tenants.apartment_id` dropped idempotently so tenant reactivation works on existing DB files
*   9 new test files — 330 automated tests passing at sprint close

One scope change during Sprint 4: the Testing Document (Element 3) was reassigned from Numair to Feras on Apr 18 after the maintenance work came in under budget and Feras had more direct manual-testing surface area (the tenant module accounts for roughly a third of the UI). The change is recorded in `docs/TEAM_RESPONSIBILITIES.md` and the Sprint 4 per-member guides.

---

## Submission Checklist (from brief.md)

### ZIP must contain:
- [x] ONE PDF with Use Case + Class + Sequence diagrams — `diagrams.pdf` (23 pages A3)
- [x] All source code (`.py` files with student ID + name headers)
- [x] `requirements.txt` (output of `pip list`)
- [x] `README.txt` with run instructions + passwords
- [ ] SQLite database with mock data (`pams.db`) — regenerate via `seed_db.py` just before ZIP
- [ ] Testing Document PDF (test cases table + screenshots) — Feras
- [ ] Agile Practices Report PDF (methodology + Git evidence) — Omar compiles

### Critical Rules:
- [x] All `.py` files must have student ID and name at the top
- [ ] NO Python distribution folder (venv) in ZIP — checked at packaging time
- [x] All diagrams in ONE PDF (not separate files!)
- [ ] All 4 members upload individually
- [ ] All 4 members present at Demo/Viva
- [x] ZIP naming: `Group28_StudentID.zip` — per-member at upload

---

## Mark Breakdown (What We're Targeting)

| Element | Marks | Target | Status |
|---------|-------|--------|--------|
| Use Case Diagram | 10 | 8.6-10 | ✅ Exported to `diagrams.pdf` |
| Class Diagram | 10 | 8.6-10 | ✅ Verified; 29 classes exported |
| Sequence Diagrams (4) | 15 | 12.76-15 | ✅ 4 flows (login, register tenant, record payment, early termination) |
| Implementation | 30 | 25.6-30 | ✅ 330 passing tests, redesigned UI |
| Testing | 10 | 8.6-10 | 🔜 Feras — Testing Document PDF |
| **Portfolio Total** | **75** | **64-75** | |
| Demo | 15 | 12-15 | 🔜 Rehearsals pending |
| Individual Q&A | 10 | 8-10 | 🔜 Each member prepares |
| **Demo/Viva Total** | **25** | **20-25** | |
| **GRAND TOTAL** | **100** | **84-100** | 🎯 |
