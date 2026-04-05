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

---

## Non-Functional Requirements (All)
*   [x] **Security**: Password hashing (bcrypt), role-based access, input validation, SQL injection prevention.
*   [x] **Mock Data**: Seed database with realistic test data for demo.

### Documentation (Sprint 3-4)
*   [ ] **Use Case Diagram**: One diagram capturing all system functionality. (Feras)
*   [ ] **Class Diagram**: UML class diagram of the system. (Omar)
*   [ ] **Sequence Diagram**: UML sequence diagrams for key flows. (All)
*   [ ] **Testing Document**: Test case table with screenshots of pass/fail. (Numair)
*   [ ] **Agile Practices Report**: PDF with Scrum evidence, Git log, sprint reviews. (Omar)
*   [ ] **Code Headers**: All .py files must include student ID and student name. (All)
