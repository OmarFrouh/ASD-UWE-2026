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
*   [x] **Maintenance Cost Report**: As a Manager, I want to track maintenance costs per apartment and per city for budget management. (Omar + Numair)

### Notifications (Sprint 2)
*   [x] **Late Payment Notification**: As a System, I want to generate a notification if the payment is late, showing tenant contact info. (Ahmed)
*   [x] **Maintenance Date Communication**: As a Staff, I want to notify tenants of scheduled maintenance dates and times. (Numair)
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

## Sprint 3 — Missing Brief Requirements + Testing ✅ (Complete — merged to dev)

### Tenant Updates (Sprint 3 — Feras)
*   [x] **Update Tenant Records**: As a Front-desk Staff, I want to edit tenant info (name, phone, email, occupation, etc.) so records stay current. (Feras)
*   [x] **1-Month Notice Period**: As a System, I want to enforce a 1-month notice period on early termination, setting the effective date to 30 days from request. (Feras)
*   [x] **Complaint Logs**: As a Front-desk Staff, I want to log, view, and resolve tenant complaints so they are tracked in the system. (Feras)

### Billing Receipts (Sprint 3 — Ahmed)
*   [x] **Payment Receipts**: As a Finance Manager, I want to see a billing/dues receipt after recording a payment, showing tenant, invoice, and payment details. (Ahmed)

### Testing & Infrastructure (Sprint 3 — Omar + Numair)
*   [x] **Complaints Table**: Add `complaints` table to database schema. (Omar)
*   [x] **Sprint 3 Seed Data**: Add complaint test data to seed_db.py. (Omar)
*   [x] **Sprint 3 Unit Tests**: Automated tests for update tenant, complaints, notice period, receipts. (Omar)
*   [x] **Sprint 3 Edge-Case Tests**: 16 tests covering complaint isolation, update field targeting, notice period boundaries. (Numair)

---

## Sprint 4 — Final Submission Prep + UI Redesign (Apr 13–23)

### UI Redesign ✅ (Omar — merged to dev 17 Apr)
*   [x] **Design Tokens**: `views/theme.py` — single source of truth for colors, fonts, spacing, radii. (Omar)
*   [x] **Sidebar Nav**: Active-state highlight with 3 px left border and muted fill. (Omar)
*   [x] **Header Bar**: Brand + dynamic page title + user chip + notification bell + logout icon. (Omar)
*   [x] **Toast Notifications**: `show_success/error/warning/info` replace every `messagebox.*` call. (Omar)
*   [x] **Custom Confirm Dialog**: `confirm_dialog()` replaces `askyesno` so prompts inherit dark theme. (Omar)
*   [x] **Dashboard**: KPI tiles + recent activity + alerts. (Omar)
*   [x] **Status/Priority Pills**: Treeview rows render status and priority as colored badges. (Omar)
*   [x] **Empty States**: Every table shows a centered empty-state message when no rows. (Omar)
*   [x] **Notification Dropdown**: Bell click opens inline dropdown anchored below the icon. (Omar)
*   [x] **Keyboard Shortcuts**: `Ctrl+R`, `Ctrl+F`, `Ctrl+L`, `F11`, `Escape`, `Alt+1..7`. (Omar)
*   [x] **Receipt Popup Redesign**: Dark-themed `CTkToplevel` with sectioned cards. (Omar)

### Sprint 4 Backend + Tests ✅ (Team — merged to dev 17 Apr)
*   [x] **PDF Generator**: `views/pdf_generator.py` — fpdf2 PDF export for invoices and receipts. (Omar)
*   [x] **fpdf2 Dependency**: Added `fpdf2==2.8.7` to `requirements.txt`. (Omar)
*   [x] **DB Migration**: `_apply_migrations()` drops legacy `UNIQUE` constraint on `tenants.apartment_id`. (Omar)
*   [x] **Tenant Login Block**: `login_view.handle_login()` rejects tenant role with "Staff use only" message. (Omar)
*   [x] **Tenant Reactivation**: `tenant_manager.reactivate_tenant()` allows archived/terminated tenants to return. (Feras)
*   [x] **Invoice Search**: `invoice_manager.search_invoices()` — filter by tenant name or invoice ID. (Ahmed)
*   [x] **CSV Export**: `report_manager.export_to_csv()` for occupancy, financial, and maintenance reports. (Omar)
*   [x] **Extended Coverage**: 9 new test files bring total from 189 → **330 passing tests**. (Team)

### Submission Deliverables (Sprint 4 — Outstanding)
*   [x] **Student ID Headers**: All `.py` files include correct student name and ID. (Omar — done 13 Apr)
*   [x] **README.txt**: Run instructions + all test passwords. (Omar — done 16 Apr)
*   [x] **requirements.txt**: Refreshed from venv with fpdf2 added. (Omar — done 17 Apr)
*   [x] **Use Case Diagram**: 5 actors + 34 use cases + `<<include>>`/`<<extend>>`. (Omar — done 18 Apr, packed into `diagrams.pdf`)
*   [x] **Class Diagram**: 29 classes across Core/Managers/Entities/Views/Utilities incl. `theme`/`ui_helpers`/`pdf_generator`. (Omar — done 18 Apr)
*   [x] **Sequence Diagrams**: 4 flows — login, register tenant, record payment (with receipt PDF branch), early termination. (Omar — done 18 Apr)
*   [x] **diagrams.pdf**: One PDF (23 pages, A3, 2.2 MB) at project root, gitignored, goes straight into submission ZIP. (Omar — done 18 Apr)
*   [x] **Merge dev → main**: Tag `submission-final`. (Omar — done 19 Apr)
*   [x] **Repo cleanup**: Drop dead `test_auth.py`, untrack Sprint 2 guides, refresh design + timeline docs. (Omar — done 19 Apr)
*   [ ] **Agile Practices Report PDF**: Scrum evidence, Git log, sprint reviews, contributions. (Omar compiles + all team sections)
*   [ ] **Testing Document PDF**: Test case table + screenshots + 330-test automated results. (Feras)
*   [ ] **Regenerate `pams.db`**: Run `seed_db.py` immediately before ZIP so the DB matches the final schema + seed. (Omar)
*   [ ] **Submission ZIP**: Build `Group28_<StudentID>.zip` and upload individually to Blackboard. (All)
*   [ ] **Demo/Viva Rehearsal**: Full walkthrough with all 5 test accounts. (All)

---

## Non-Functional Requirements (All)
*   [x] **Security**: Password hashing (bcrypt), role-based access, input validation, SQL injection prevention.
*   [x] **Mock Data**: Seed database with realistic test data for demo.
