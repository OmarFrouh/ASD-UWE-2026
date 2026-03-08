# Team Roles & Responsibilities Matrix

**Purpose**: This document tracks who is "Captain" of which section.
**Rule**: The "Owner" has the final say on the code in their section.

## 1. 👑 Omar Alfrouh (Group Leader)
*   **Role**: Scrum Master & Core Architect
*   **Responsibility**:
    *   **The Backbone**: Ensuring the database, authentication, and main window work.
    *   **Code Review**: Merging everyone else's Pull Requests.
    *   **System Design**: Owning the Class Diagram.
*   **Assigned Tasks**:
    *   [x] Create Project Repo & Git Rules
    *   [x] Design Class Diagram (Astah)
    *   [x] Implement `DatabaseManager` (SQLite)
    *   [x] **Design**: Draft Sequence Diagrams (Astah)
    *   [x] Implement `AuthManager` (Login/Logout Logic)
    *   [x] Build `MainView` (The Shell/Navigation)
    *   [x] Implement `PropertyManager` (Apartment Logic)
    *   [x] Build `ApartmentView` (Add/List Apartments)

## 2. 🎨 Feras Bader
*   **Role**: Frontend Lead & Product Owner
*   **Responsibility**:
    *   **UI Consistency**: Making sure all forms look the same.
    *   **Tenant Operations**: Everything related to people living in the building.
*   **Assigned Tasks**:
    *   [ ] **Design**: Draw the **Use Case Diagram** (Astah)
    *   [ ] Build `TenantRegistrationView` (Add Tenant Form - NI, Name, Phone, Email, Occupation, References)
    *   [ ] Build `TenantListView` (Search/Filter Tenants)
    *   [ ] Build `LeaseManager` (Renew/Cancel Lease logic)
    *   [ ] Build `EarlyTerminationHandler` (Process early leave with 5% penalty)

## 3. 💸 Ahmed Deraz
*   **Role**: Finance Lead
*   **Responsibility**:
    *   **Money**: Invoices, Payments, and Totals.
    *   **Privacy**: Ensuring only authorized users see financial data.
*   **Assigned Tasks**:
    *   [ ] Build `InvoiceGenerator` (Create Bills)
    *   [ ] Build `PaymentProcessing` (Record Payments)
    *   [ ] Build `LatePaymentTracker` (Flag overdue tenants)
    *   [ ] Build `FinancialReportGenerator` (Collected vs Pending rents)

## 4. 🔧 Numair
*   **Role**: QA & Maintenance Lead
*   **Responsibility**:
    *   **Testing**: Ensuring bugs are found before submission.
    *   **Maintenance**: The ticketing system for repairs.
*   **Assigned Tasks**:
    *   [ ] Build `MaintenanceTicketView` (Report Issues)
    *   [ ] Build `StaffAssignmentView` (Assign janitor to fix pipe)
    *   [ ] Build `MaintenanceCostLogger` (Time + Cost tracking per issue)
    *   [ ] Build `OccupancyReportView` (Chart of occupied vs empty apartments)
    *   [ ] **Test**: Run final system checks.
