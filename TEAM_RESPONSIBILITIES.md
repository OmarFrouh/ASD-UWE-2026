# Team Roles & Responsibilities Matrix

**Purpose**: This document tracks who is "Captain" of which section.
**Rule**: The "Owner" has the final say on the code in their section.
**Deadline**: 23 April 2026, 14:00

---

## 1. 👑 Omar Alfrouh (Group Leader)
*   **Role**: Scrum Master & Core Architect
*   **Responsibility**:
    *   **The Backbone**: Database, authentication, main window, and project infrastructure.
    *   **Code Review**: Merging everyone's Pull Requests.
    *   **System Design**: Owning the Class Diagram + Sequence Diagrams.
    *   **Documentation**: Agile Practices Report.
*   **Completed Tasks (Sprint 0)**:
    *   [x] Create Project Repo & Git Rules
    *   [x] Design Class Diagram (Astah) - Verified 100%
    *   [x] Design 3 Sequence Diagrams (Astah) - Verified 100%
    *   [x] Implement `DatabaseManager` (SQLite schema)
    *   [x] Implement `AuthManager` (Login, Create User, bcrypt)
    *   [x] Build `MainView` (Shell, Sidebar, Role Permissions)
    *   [x] Implement `PropertyManager` (Add/List Apartments)
    *   [x] Build `LoginView`, `UserView`, `ApartmentView`
*   **Remaining Tasks**:
    *   [ ] **Sprint 1-2**: Code review all PRs, unblock team
    *   [ ] **Sprint 2**: Wire all new views into `MainView` sidebar
    *   [ ] **Sprint 3**: Write Agile Practices Report (PDF)
    *   [ ] **Sprint 3**: Security audit (input validation, SQL injection)
    *   [ ] **Sprint 3**: Update mock data seed script
    *   [ ] **Sprint 4**: Export all diagrams to ONE PDF
    *   [ ] **Sprint 4**: Add student ID + name headers to all .py files
    *   [ ] **Sprint 4**: Create final ZIP (`Group28_StudentID.zip`)
    *   [ ] **Sprint 4**: Include `requirements.txt` + run instructions

---

## 2. 🎨 Feras Bader (Frontend Lead)
*   **Role**: Frontend Lead & Product Owner
*   **Responsibility**:
    *   **UI Consistency**: Making sure all forms look the same.
    *   **Tenant Operations**: Everything related to tenants and leases.
    *   **Use Case Diagram**: Designing the system use case diagram.
*   **Sprint 1 Tasks** (Mar 31 - Apr 6):
    *   [ ] Draw **Use Case Diagram** in Astah
    *   [ ] Build `tenant_manager.py` (add, update, remove, archive tenant)
    *   [ ] Build `TenantRegistrationView` (NI, Name, Phone, Email, Occupation, References, Apt Requirements, Lease Period)
    *   [ ] Build `lease_manager.py` (start/end dates, renew, early termination with 5% penalty)
*   **Sprint 2 Tasks** (Apr 7 - Apr 13):
    *   [ ] Build `TenantListView` (search, filter, update, remove)
    *   [ ] Build `AssignTenantToApartment` (link tenant → apartment, update occupancy status)
    *   [ ] Build `ArchiveTenantView` (move tenant to inactive)
*   **Sprint 3 Tasks** (Apr 14 - Apr 18):
    *   [ ] Polish UI consistency across all tenant forms
    *   [ ] Write test cases for tenant features

---

## 3. 💸 Ahmed Deraz (Finance Lead)
*   **Role**: Finance Lead
*   **Responsibility**:
    *   **Money**: Invoices, Payments, and Financial Reports.
    *   **Privacy**: Ensuring only Finance Manager/Admin sees financial data.
*   **Sprint 1 Tasks** (Mar 31 - Apr 6):
    *   [ ] Build `invoice_manager.py` (generate monthly rent bill as PDF/text)
    *   [ ] Build `InvoiceView` (create invoice form + invoice list)
    *   [ ] Build `payment_manager.py` (record payments against invoices)
    *   [ ] Build `PaymentView` (payment form + history)
*   **Sprint 2 Tasks** (Apr 7 - Apr 13):
    *   [ ] Build `LatePaymentTracker` (flag overdue + notification)
    *   [ ] Build `FinancialReportView` (collected vs pending rents, chart)
*   **Sprint 3 Tasks** (Apr 14 - Apr 18):
    *   [ ] Input validation on all finance forms
    *   [ ] Write test cases for finance features

---

## 4. 🔧 Numair (QA & Maintenance Lead)
*   **Role**: QA & Maintenance Lead
*   **Responsibility**:
    *   **Maintenance**: The full ticketing lifecycle (report → assign → resolve → log costs).
    *   **Reporting**: Occupancy and maintenance cost reports.
    *   **Testing**: Creating the testing document with evidence.
*   **Sprint 1 Tasks** (Mar 31 - Apr 6):
    *   [ ] Build `maintenance_manager.py` (report issue, set priority, update status)
    *   [ ] Build `MaintenanceTicketView` (report form + ticket list)
    *   [ ] Build staff assignment logic (check availability, assign worker)
*   **Sprint 2 Tasks** (Apr 7 - Apr 13):
    *   [ ] Build `MaintenanceCostLogger` (log time + costs per resolved issue)
    *   [ ] Build maintenance date communication (notify tenant)
    *   [ ] Build `OccupancyReportView` (chart: occupied vs empty by location)
    *   [ ] Build `MaintenanceCostReport` (budget tracking view)
*   **Sprint 3 Tasks** (Apr 14 - Apr 18):
    *   [ ] Create **Testing Document** (test case table format from brief)
    *   [ ] Run automated tests (pytest) + capture pass/fail screenshots
    *   [ ] Write evidence for manual testing
