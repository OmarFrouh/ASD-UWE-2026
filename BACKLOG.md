# Product Backlog

*Copy and paste each of these items as a separate "New Issue" in the GitHub 'Issues' tab.*

## User Stories (Features)

### User Management ✅ (Omar - Sprint 1 Complete)
*   [x] **Login System**: As an Administrator, I want to log in securely so that unauthorized users cannot access sensitive data.
*   [x] **Create Accounts**: As an Admin, I want to create accounts for Staff members so they can do their jobs.
*   [x] **Role Permissions**: As a System, I want to hide Financial tabs from Maintenance users so that data privacy is maintained.

### Tenant Management ✅ (Feras - Sprint 1 Complete)
*   [x] **Register Tenant**: As a Front-desk Staff, I want to add a new tenant (NI Number, Name, Phone, Email, Occupation, References, Apartment Requirements, Lease Period) so they are registered in the system.
*   [x] **Tenant List**: As a Front-desk Staff, I want to view tenant records.
*   [x] **Manage Leases**: As a Front-desk Staff, I want to set a lease start and end date for a tenant.
*   [x] **Early Termination**: As a Front-desk Staff, I want to process early lease termination (1 month notice + 5% of monthly rent penalty) so tenants can leave before contract end.
*   [x] **Archive Tenant**: As a Manager, I want to archive tenants who have moved out so the active list remains clean.

### Apartment Management ✅ (Omar - Sprint 1 Complete)
*   [x] **Add Apartment**: As an Admin, I want to register a new apartment (Location, Type, Monthly Rent, Number of Rooms).
*   [x] **Assign Tenant**: As a Staff, I want to link a Tenant to a specific Apartment to track occupancy. (Feras)

### Finance ✅ (Ahmed - Sprint 1 Complete)
*   [x] **Generate Invoice**: As a Finance Manager, I want to create an invoice for a tenant's monthly rent.
*   [x] **Record Payment**: As a Finance Manager, I want to record payments against invoices to track what's been paid.
*   [x] **Track Late Payments**: As a System, I want to flag tenants who are late on payment.

### Maintenance ✅ (Numair - Sprint 1 Complete)
*   [x] **Log Issue**: As a Front-desk Staff, I want to record a maintenance issue reported by a tenant with priority level.
*   [x] **Assign Staff**: As a Manager, I want to assign a maintenance worker to an issue based on availability.
*   [x] **Update Status**: As a Maintenance Worker, I want to mark an issue as "In Progress" or "Fixed".
*   [x] **Log Costs**: As a Maintenance Worker, I want to record time spent and costs for each repair.

---

## Sprint 2 — Reporting, Notifications & Enhancements

### Reporting (Sprint 2)
*   [x] **Occupancy Report**: As a Manager, I want to see how many apartments are occupied vs empty, filtered by city. (Omar)
*   [x] **Financial Summary**: As a Manager, I want to see collected vs pending rent totals with per-tenant breakdown. (Omar + Ahmed)
*   [ ] **Maintenance Cost Report**: As a Manager, I want to track maintenance costs per apartment and per city for budget management. (Omar + Numair)

### Notifications (Sprint 2)
*   [x] **Late Payment Notification**: As a System, I want to generate a notification if the payment is late, showing tenant contact info. (Ahmed)
*   [ ] **Maintenance Date Communication**: As a Staff, I want to notify tenants of scheduled maintenance dates and times. (Numair)
*   [x] **Expiring Lease Alerts**: As a System, I want to flag tenants whose leases expire within 30 days. (Omar)

### Tenant Enhancements (Sprint 2)
*   [x] **Search Tenants**: As a Front-desk Staff, I want to search tenants by name, NI, email, or phone. (Feras)
*   [x] **Filter by Status**: As a Front-desk Staff, I want to filter the tenant list by Active/Archived/Terminated. (Feras)

### Finance Enhancements (Sprint 2)
*   [x] **Overdue Badges**: As a Finance Manager, I want to see visual overdue markers on unpaid invoices. (Ahmed)
*   [x] **Payment Method Breakdown**: As a Finance Manager, I want to see payment totals by method (Card/Cash/Transfer). (Ahmed)

### Sprint 2 QA Fixes (Omar — Complete)
*   [x] **Notification Badge**: Clickable badge in header showing overdue invoices + expiring leases. (Omar)
*   [x] **Dynamic City Dropdown**: Apartment form city list queries DB, not hardcoded. (Omar)
*   [x] **User List Treeview**: USR-01 — users table added to Users tab. (Omar)
*   [x] **Required Field Markers**: `*` on all mandatory fields system-wide. (Omar)
*   [x] **App Resizable**: Full window resize + fullscreen support. (Omar)
*   [x] **Form Scrolling**: CTkScrollableFrame on all form-heavy views. (Omar)
*   [x] **Maintenance Cost Report**: Per-apartment and per-city cost tables in Maintenance tab. (Numair)
*   [x] **Maintenance Date Communication**: Set scheduled date + show tenant contact info. (Numair)

---

## Sprint 3 — Missing Brief Requirements + Testing (Apr 14–18)

### Tenant Updates (Sprint 3 — Feras)
*   [ ] **Update Tenant Records**: As a Front-desk Staff, I want to edit tenant info (name, phone, email, occupation, etc.) so records stay current. (Feras)
*   [ ] **1-Month Notice Period**: As a System, I want to enforce a 1-month notice period on early termination, setting the effective date to 30 days from request. (Feras)
*   [ ] **Complaint Logs**: As a Front-desk Staff, I want to log, view, and resolve tenant complaints so they are tracked in the system. (Feras)

### Billing Receipts (Sprint 3 — Ahmed)
*   [ ] **Payment Receipts**: As a Finance Manager, I want to see a billing/dues receipt after recording a payment, showing tenant, invoice, and payment details. (Ahmed)

### Testing & Infrastructure (Sprint 3 — Omar + Numair)
*   [ ] **Complaints Table**: Add `complaints` table to database schema. (Omar)
*   [ ] **Sprint 3 Seed Data**: Add complaint test data to seed_db.py. (Omar)
*   [ ] **Sprint 3 Unit Tests**: Automated tests for update tenant, complaints, notice period, receipts. (Omar)
*   [ ] **Testing Document PDF**: Formal test case table with screenshots of pass/fail for all sprints. (Numair)

---

## Non-Functional Requirements (All)
*   [x] **Security**: Password hashing (bcrypt), role-based access, input validation, SQL injection prevention.
*   [x] **Mock Data**: Seed database with realistic test data for demo.

### Documentation (Sprint 4)
*   [ ] **Use Case Diagram**: One diagram capturing all system functionality. (Feras)
*   [ ] **Class Diagram**: UML class diagram of the system. (Omar)
*   [ ] **Sequence Diagram**: UML sequence diagrams for key flows. (All)
*   [ ] **Agile Practices Report**: PDF with Scrum evidence, Git log, sprint reviews. (Omar)
*   [ ] **Code Headers**: All .py files must include student ID and student name → `24020879` for Omar's 10 files. (All)
