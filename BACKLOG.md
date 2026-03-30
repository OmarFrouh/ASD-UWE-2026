# Product Backlog

*Copy and paste each of these items as a separate "New Issue" in the GitHub 'Issues' tab.*

## User Stories (Features)

### User Management ✅ (Omar - Complete)
*   **Login System**: As an Administrator, I want to log in securely so that unauthorized users cannot access sensitive data. ✅
*   **Create Accounts**: As an Admin, I want to create accounts for Staff members so they can do their jobs. ✅
*   **Role Permissions**: As a System, I want to hide Financial tabs from Maintenance users so that data privacy is maintained. ✅

### Tenant Management (Feras)
*   **Register Tenant**: As a Front-desk Staff, I want to add a new tenant (NI Number, Name, Phone, Email, Occupation, References, Apartment Requirements, Lease Period) so they are registered in the system.
*   **Tenant List**: As a Front-desk Staff, I want to search, filter, update and remove tenant records.
*   **Manage Leases**: As a Front-desk Staff, I want to set a lease start and end date for a tenant.
*   **Early Termination**: As a Front-desk Staff, I want to process early lease termination (1 month notice + 5% of monthly rent penalty) so tenants can leave before contract end.
*   **Archive Tenant**: As a Manager, I want to archive tenants who have moved out so the active list remains clean.

### Apartment Management
*   **Add Apartment**: As an Admin, I want to register a new apartment (Location, Type, Monthly Rent, Number of Rooms). ✅
*   **Assign Tenant**: As a Staff, I want to link a Tenant to a specific Apartment to track occupancy. (Feras)

### Finance (Ahmed)
*   **Generate Invoice**: As a Finance Manager, I want to create a PDF or Text invoice for a tenant's monthly rent.
*   **Record Payment**: As a Finance Manager, I want to record payments against invoices to track what's been paid.
*   **Track Late Payments**: As a System, I want to flag tenants who are late on payment and generate a notification.
*   **Financial Reports**: As a Finance Manager, I want to generate reports comparing collected vs pending rents.

### Maintenance (Numair)
*   **Log Issue**: As a Front-desk Staff, I want to record a maintenance issue reported by a tenant with priority level.
*   **Assign Staff**: As a Manager, I want to assign a maintenance worker to an issue based on availability.
*   **Update Status**: As a Maintenance Worker, I want to mark an issue as "In Progress" or "Fixed".
*   **Log Costs**: As a Maintenance Worker, I want to record time spent and costs for each repair.
*   **Communicate Dates**: As a Staff, I want to notify tenants of scheduled maintenance dates.

### Reporting (Numair + Ahmed)
*   **Occupancy Report**: As a Manager, I want to see a chart of how many apartments are occupied vs empty, filtered by location.
*   **Financial Summary**: As a Manager, I want to see collected vs pending rent totals.
*   **Maintenance Cost Report**: As a Manager, I want to track maintenance costs for budget management.

### Non-Functional Requirements (All)
*   **Security**: Password hashing (bcrypt ✅), role-based access ✅, input validation, SQL injection prevention.
*   **Mock Data**: Seed database with realistic test data for demo.

### Documentation (Sprint 3-4)
*   **Use Case Diagram**: One diagram capturing all system functionality. (Feras)
*   **Testing Document**: Test case table with screenshots of pass/fail. (Numair)
*   **Agile Practices Report**: PDF with Scrum evidence, Git log, sprint reviews. (Omar)
*   **Code Headers**: All .py files must include student ID and student name. (All)
