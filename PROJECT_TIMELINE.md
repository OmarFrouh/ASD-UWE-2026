# 4-Sprint Master Plan
**Deadline**: 23 April 2026, 14:00 UK
**Today**: 30 March 2026
**Time Remaining**: 3.5 weeks (24 days)
**Team**: Omar (Leader), Feras Bader, Ahmed Deraz, Numair

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

### ❌ NOT YET BUILT

| # | Requirement (from brief.md) | Brief Section | Assigned |
|---|---------------------------|---------------|----------|
| 1 | **Register Tenant** (NI, name, phone, email, occupation, references, apt requirements, lease period) | Account/User Mgmt | Feras |
| 2 | **Tenant List** (search, filter, update, remove) | Tenant Mgmt | Feras |
| 3 | **Lease Manager** (start/end dates, renew, cancel) | Tenant Mgmt | Feras |
| 4 | **Early Termination** (1 month notice + 5% penalty) | Tenant Mgmt | Feras |
| 5 | **Archive Tenant** (moved out → inactive) | Tenant Mgmt | Feras |
| 6 | **Assign Tenant to Apartment** (link + track occupancy) | Apartment Mgmt | Feras |
| 7 | **Invoice Generator** (PDF/text bill for monthly rent) | Payment & Billing | Ahmed |
| 8 | **Payment Processing** (record payments, emulate process) | Payment & Billing | Ahmed |
| 9 | **Late Payment Tracker** (flag overdue + notification) | Payment & Billing | Ahmed |
| 10 | **Financial Reports** (collected vs pending rents) | Reporting | Ahmed |
| 11 | **Maintenance Ticket** (report issue, prioritise, assign) | Maintenance | Numair |
| 12 | **Staff Assignment** (check availability, assign worker) | Maintenance | Numair |
| 13 | **Maintenance Cost Logger** (time + costs per issue) | Maintenance | Numair |
| 14 | **Communicate Dates** (notify tenant of maintenance date) | Maintenance | Numair |
| 15 | **Occupancy Report** (chart by apartment/city) | Reporting | Numair |
| 16 | **Maintenance Cost Report** (budget tracking) | Reporting | Numair |
| 17 | **Use Case Diagram** | Element 1 | Feras |
| 18 | **Testing Document** (test cases table + screenshots) | Element 3 | Numair |
| 19 | **Agile Practices Report** (PDF, methodology evidence) | Element 2 | Omar |
| 20 | **Mock Data** (seed DB for demo) | Element 2 | Omar |
| 21 | **Non-functional: Security** (bcrypt ✅, role-based ✅, input validation) | Element 2 | All |

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

---

### Sprint 3: Apr 14 - Apr 18 (Meeting 3)
**Focus**: Testing + Documentation + Polish

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **Feras** | Polish UI consistency across all forms | Clean UI |
| **Feras** | Help with test cases for Tenant features | Test rows |
| **Ahmed** | Input validation on all finance forms | Robust forms |
| **Ahmed** | Help with test cases for Finance features | Test rows |
| **Numair** | Create **Testing Document** (test case table + screenshots) | `TESTING.pdf` |
| **Numair** | Run automated tests (pytest) + capture screenshots | Evidence |
| **Omar** | Write **Agile Practices Report** (Scrum evidence, Git log, sprint reviews) | `AGILE_REPORT.pdf` |
| **Omar** | Final bug fixes, security audit (input validation, SQL injection prevention) | Hardened code |
| **All** | Merge all branches, resolve conflicts | Clean `main` |

---

### Sprint 4: Apr 19 - Apr 22 (Meeting 4)
**Focus**: Submission Prep + Demo Rehearsal

| Owner | Tasks | Deliverable |
|-------|-------|-------------|
| **All** | Demo rehearsal (each member explains their part) | Practice run |
| **Omar** | Export diagrams to ONE PDF (Use Case + Class + Sequence) | `diagrams.pdf` |
| **Omar** | Add student IDs + names to all `.py` files (brief requirement!) | Header comments |
| **Omar** | Create final ZIP: `Group28_StudentID.zip` | Submission package |
| **Omar** | Include `requirements.txt` (`pip list`) and `README` with run instructions | Setup docs |
| **All** | Each member uploads the ZIP individually on Blackboard | ✅ Submitted |
| **Apr 23** | **DEADLINE 14:00** | 🚨 |

---

## Submission Checklist (from brief.md)

### ZIP must contain:
- [ ] ONE PDF with Use Case + Class + Sequence diagrams
- [ ] All source code (`.py` files with student ID + name headers)
- [ ] `requirements.txt` (output of `pip list`)
- [ ] `README.txt` with run instructions + passwords
- [ ] SQLite database with mock data (`pams.db`)
- [ ] Testing Document PDF (test cases table + screenshots)
- [ ] Agile Practices Report PDF (methodology + Git evidence)

### Critical Rules:
- [ ] All `.py` files must have student ID and name at the top
- [ ] NO Python distribution folder (venv) in ZIP
- [ ] All diagrams in ONE PDF (not separate files!)
- [ ] All 4 members upload individually
- [ ] All 4 members present at Demo/Viva
- [ ] ZIP naming: `Group28_StudentID.zip`

---

## Mark Breakdown (What We're Targeting)

| Element | Marks | Target | Status |
|---------|-------|--------|--------|
| Use Case Diagram | 10 | 8.6-10 | Feras drawing |
| Class Diagram | 10 | 8.6-10 | ✅ Verified 100% |
| Sequence Diagrams (3) | 15 | 12.76-15 | ✅ Verified 100% |
| Implementation | 30 | 25.6-30 | 🔄 Building |
| Testing | 10 | 8.6-10 | Numair creating |
| **Portfolio Total** | **75** | **64-75** | |
| Demo | 15 | 12-15 | Rehearse Sprint 4 |
| Individual Q&A | 10 | 8-10 | Each member prepares |
| **Demo/Viva Total** | **25** | **20-25** | |
| **GRAND TOTAL** | **100** | **84-100** | 🎯 |
