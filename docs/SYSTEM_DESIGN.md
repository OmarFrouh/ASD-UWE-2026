# System Design Specifications (Final Universal Notation)

This document is the **design spec** that sits alongside the exported class diagram (`diagrams/Class Diagram/ClassDiagramFinal.png` / `.svg`, packed into `diagrams.pdf`). It is the written view of the same design the diagram shows.

**Notation Rules Used:**
*   `int` (not Integer)
*   `double` (not Float/Decimal, for currency)
*   `boolean` (not Boolean)
*   `String` (Standard text type)
*   `List<Type>` (for collections)

**Design changes from the Sprint 0 spec to the final delivered system are called out inline.** The Astah diagram matches this final spec.

---

## 1. Class Definitions

The final diagram groups classes into five layers: **Core**, **Managers**, **Entities** (database-backed), **Views** (CustomTkinter UI), and **Utilities**. The manager layer replaces the original single-controller design after Sprint 1 showed the controller would have owned eight distinct concerns.

### 1.1 Core System

**Class: `DatabaseManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- db_path : String` | **Type `String`**: SQLite database file path. |
| **Operations** | |
| `+ execute_query(sql: String, params: List) : void` | Parameterised write query. |
| `+ fetch_all(sql: String, params: List) : List<Tuple>` | Parameterised read query. |
| `+ create_tables() : void` | Runs schema creation DDL (idempotent). |
| `- _apply_migrations() : void` | Idempotent migrations — currently drops the legacy `UNIQUE` constraint on `tenants.apartment_id` so reactivated tenants can move into previously-used units. |

**Class: `AuthManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- db : DatabaseManager` | Shared DB handle. |
| `- current_user : Tuple` | Current session row `(id, username, hash, role, created_at, last_login)`. |
| **Operations** | |
| `+ login(username: String, password: String) : Tuple` | Returns the user row on success, `None` on failure. |
| `+ logout() : void` | Clears `current_user`. |
| `+ create_user(user: String, pass: String, role: String, empID: String, dept: String) : boolean` | Transactional creation of user + staff row (staff row only for non-tenant roles). |
| `+ create_tenant_user(...) : int` | Transactional creation of user + tenant row; returns new user id. |
| `+ reset_password(user_id: int, new_password: String) : boolean` | Admin helper. |
| `+ update_user(user_id: int, **fields) : boolean` | Partial user update. |
| `+ delete_user(user_id: int) : boolean` | FK-cascaded delete. |
| `+ get_all_users() : List<Tuple>` | Full user listing for the Users tab. |
| `+ get_dashboard_stats() : Dict<String, int>` | KPI data for the dashboard tiles. |

### 1.2 Managers (replaces the single-controller Sprint 0 design)

**Class: `TenantManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ register_tenant(ni, name, ...) : int` | Creates tenant record, returns user id. |
| `+ assign_apartment(tenant_id: int, apt_id: int) : void` | Sets apartment on tenant + flips apartment status to `Occupied`. |
| `+ early_termination(tenant_id: int) : Dict` | Returns `{"penalty": double, "effective_date": Date}` — dict shape added in Sprint 3 when the 1-month notice period was introduced. |
| `+ archive_tenant(tenant_id: int) : void` | Status → Archived, apartment vacated. |
| `+ reactivate_tenant(tenant_id: int, apt_id: int, ...) : void` | Sprint 4 — brings an archived/terminated tenant back into service. |
| `+ update_tenant(tenant_id: int, **fields) : boolean` | Sprint 3 — partial update using kwargs; only touches fields that are not `None`. |
| `+ get_tenant_by_id(tenant_id: int) : Tuple` | Sprint 3 — read-one for the Edit tab. |
| `+ search_tenants(query: String) : List<Tuple>` | Search by name / NI / email / phone. |
| `+ filter_tenants_by_status(status: String) : List<Tuple>` | List filtered by `Active` / `Archived` / `Terminated`. |
| `+ log_complaint(tenant_id: int, subject: String, description: String) : int` | Sprint 3 — returns complaint id. |
| `+ get_all_complaints() : List<Tuple>` | Sprint 3. |
| `+ resolve_complaint(complaint_id: int) : boolean` | Sprint 3. |

**Class: `PropertyManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ add_apartment(unit: String, city: String, rent: double, rooms: int, sqft: int) : int` | Creates apartment, returns id. |
| `+ list_apartments(status: String) : List<Tuple>` | Filter by Vacant / Occupied / All. |
| `+ get_cities() : List<String>` | Feeds the dynamic city dropdown. |
| `+ update_status(apt_id: int, status: String) : void` | Sets Vacant / Occupied. |

**Class: `InvoiceManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ generate_invoice(tenant_id: int, amount: double) : int` | Returns new invoice id. |
| `+ get_overdue_with_details() : List<Tuple>` | Overdue invoices with tenant contact info for the Late Payment tab. |
| `+ get_invoice_aging() : List<Tuple>` | Aging bucket summary. |
| `+ search_invoices(query: String) : List<Tuple>` | Sprint 4 — filter by tenant name or invoice id. |

**Class: `PaymentManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ record_payment(invoice_id: int, amount: double, method: String, ref: String) : int` | Atomic: insert payment row + flip invoice to `Paid` if cumulative sum ≥ total. Returns new payment id (Sprint 3 change, for receipt rendering). |
| `+ get_receipt_data(payment_id: int) : Dict` | Sprint 3 — bundles tenant / property / invoice / payment for the receipt modal. |
| `+ get_collected_vs_pending() : Dict` | Financial summary tile data. |
| `+ get_payment_history_by_method() : List<Tuple>` | Method breakdown table. |
| `+ get_monthly_revenue() : List<Tuple>` | Month-by-month revenue chart data. |

**Class: `MaintenanceManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ create_ticket(apt_id: int, tenant_id: int, desc: String, priority: String) : int` | Returns ticket id. |
| `+ assign_staff(ticket_id: int, staff_id: int) : void` | Sets assigned staff + status to `Assigned`. |
| `+ update_status(ticket_id: int, status: String) : void` | Workflow: Open → Assigned → In Progress → Fixed → Closed. |
| `+ log_cost(ticket_id: int, amount: double, hours: double) : void` | Cumulative — adds to any existing cost/hours. |
| `+ notify_tenant_scheduled_date(ticket_id: int, date: Date) : Dict` | Returns the tenant contact info bundle for the Notify Tenant section. |
| `+ get_cost_report_by_apartment() : List<Tuple>` | Per-apartment totals. |
| `+ get_cost_report_by_city() : List<Tuple>` | Per-city totals. |
| `+ get_tickets_by_status_count() : Dict` | Summary card data. |

**Class: `ReportManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ get_occupancy_report(city: String) : Dict` | Totals + per-apartment rows. |
| `+ get_financial_summary() : Dict` | Collected / pending totals + per-tenant table. |
| `+ get_maintenance_cost_report(city: String) : Dict` | Per-apartment and per-city cost breakdown. |
| `+ export_to_csv(report_name: String, rows: List) : String` | Sprint 4 — writes a CSV to `~/Downloads/` and returns the path. |

**Class: `NotificationManager`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Operations** | |
| `+ get_overdue_invoices() : List<Tuple>` | For the bell dropdown. |
| `+ get_expiring_leases(days: int) : List<Tuple>` | Leases expiring within window. |
| `+ get_upcoming_maintenance() : List<Tuple>` | Scheduled tickets. |
| `+ get_notification_count() : int` | Badge number. |
| `+ get_notifications() : List<Dict>` | Combined feed for the dropdown. |

### 1.3 Entities (database-backed, represented as table rows)

In the final implementation these are not subclasses — they are rows in SQLite tables. The original Sprint 0 spec modelled `Admin`, `Staff`, and `Tenant` as subclasses of `User`; in Python with SQLite we kept the inheritance relationship in the **Class Diagram** (for submission) but implemented it via a `role` column + a `staff` / `tenants` child table. This is the standard relational translation and is noted as such on the diagram.

**Entity: `User`**

| Attribute | Type |
| :--- | :--- |
| `- id : int` | Primary key. |
| `- username : String` | Unique. |
| `- password_hash : String` | bcrypt hash stored as `BLOB`. |
| `- role : String` | One of: `admin`, `front_desk`, `finance_manager`, `maintenance`, `manager`, `tenant`. |
| `- created_at : DateTime` | |
| `- last_login : DateTime` | |

**Entity: `Staff`** (child row for non-tenant users)

| Attribute | Type |
| :--- | :--- |
| `- user_id : int` | FK to `users.id`. |
| `- employee_id : String` | e.g. "EMP001". |
| `- department : String` | |

**Entity: `Tenant`** (child row for tenant users — currently only used as an FK target; tenant login is blocked at `login_view`)

| Attribute | Type |
| :--- | :--- |
| `- user_id : int` | FK. |
| `- ni_number : String` | National Insurance number. |
| `- full_name : String` | |
| `- phone, email, occupation, references, emergency_contact, apartment_requirements : String` | |
| `- apartment_id : int` | FK, nullable. |
| `- lease_start : Date` | |
| `- lease_end : Date` | |
| `- monthly_rent : double` | |
| `- deposit : double` | |
| `- status : String` | `Active` / `Archived` / `Terminated`. |

**Entity: `Apartment`**

| Attribute | Type |
| :--- | :--- |
| `- id : int` | |
| `- unit_number : String` | Supports "4B", "PH". |
| `- address : String` | |
| `- city : String` | |
| `- number_of_rooms : int` | |
| `- rental_price : double` | |
| `- square_footage : int` | |
| `- status : String` | "Occupied" / "Vacant". |

**Entity: `Invoice`**

| Attribute | Type |
| :--- | :--- |
| `- id : int` | |
| `- tenant_id : int` | FK. |
| `- issue_date : Date` | |
| `- due_date : Date` | |
| `- total_amount : double` | |
| `- status : String` | "Paid" / "Pending". |

**Entity: `Payment`**

| Attribute | Type |
| :--- | :--- |
| `- id : int` | |
| `- invoice_id : int` | FK. |
| `- amount : double` | |
| `- payment_date : DateTime` | |
| `- method : String` | "Card" / "Cash" / "Transfer". |
| `- transaction_ref : String` | |

**Entity: `MaintenanceRequest`**

| Attribute | Type |
| :--- | :--- |
| `- id : int` | |
| `- apartment_id : int` | FK. |
| `- tenant_id : int` | FK, nullable. |
| `- staff_id : int` | FK, nullable. |
| `- description : String` | |
| `- priority : String` | Low / Medium / High / Urgent. |
| `- status : String` | Open → Assigned → In Progress → Fixed → Closed. |
| `- scheduled_date : Date` | |
| `- date_reported : DateTime` | |
| `- date_resolved : DateTime` | Nullable. |
| `- time_spent : double` | Hours, cumulative. |
| `- cost : double` | Cumulative. |

**Entity: `Complaint`** *(added in Sprint 3)*

| Attribute | Type |
| :--- | :--- |
| `- id : int` | |
| `- tenant_id : int` | FK with `ON DELETE CASCADE`. |
| `- date_logged : DateTime` | |
| `- subject : String` | |
| `- description : String` | |
| `- status : String` | "Open" / "Resolved". |
| `- resolved_date : DateTime` | Nullable. |

### 1.4 Views (CustomTkinter UI boundary classes)

One class per screen: `LoginView`, `MainView`, `UserView`, `ApartmentView`, `TenantView`, `InvoiceView`, `PaymentView`, `MaintenanceView`, `ReportView`.

Each view holds its own widgets, wires button callbacks to the matching manager method, and uses the design tokens in `views/theme.py`. None of them touch the database directly — they call managers.

### 1.5 Utilities *(Sprint 4)*

*   **`views/theme.py`** — design tokens (colors, fonts, spacing, radii, dimensions). Single source of truth imported as `T`.
*   **`views/ui_helpers.py`** — factory functions for cards, KPI tiles, toasts, confirm dialog, badges, empty states, and the enhanced treeview (status / priority pills rendered via tag-swap).
*   **`views/pdf_generator.py`** — `fpdf2`-powered PDF invoice + receipt export.

---

## 2. Relationships (Quick Reference)

| **Source** | **Target** | **Line Type** | **Logic** |
| :--- | :--- | :--- | :--- |
| **Admin** / **Staff** / **Tenant** | **User** | **Inheritance** (White Triangle) | "Is A" User — conceptual; implemented via `role` + child tables. |
| **AuthManager** | **User / Staff / Tenant** | **Dependency** (Dashed Arrow) | Manager uses the entities. |
| **Apartment** (1) | **Tenant** (0..1) | **Association** | Occupancy. |
| **Apartment** (1) | **MaintenanceRequest** (*) | **Association** | Property history. |
| **Tenant** (1) | **Invoice** (*) | **Association** | Billing history. |
| **Tenant** (1) | **Complaint** (*) | **Composition** (Solid Diamond) | `ON DELETE CASCADE` — complaints belong to a tenant. |
| **Invoice** (1) | **Payment** (*) | **Composition** (Solid Diamond) | Payments have no meaning without their invoice. |
| **Staff** (0..1) | **MaintenanceRequest** (*) | **Association** | Assignment. |
| **View** layer | **Manager** layer | **Dependency** | Views call managers, not the DB. |
| **Manager** layer | **DatabaseManager** | **Dependency** | All DB access funnels through one class. |

---

## 3. Notable Design Changes Between Sprint 0 Spec and Final Delivery

| Change | Reason |
| :--- | :--- |
| `PAMSController` replaced by nine manager classes (`AuthManager`, `PropertyManager`, `TenantManager`, `InvoiceManager`, `PaymentManager`, `MaintenanceManager`, `ReportManager`, `NotificationManager`, `DatabaseManager`). | A single controller would have owned ~50 methods. Splitting by domain keeps each file under 300 lines and makes PR review cleaner. |
| `Admin` / `Staff` / `Tenant` became a `role` column + `staff` / `tenants` child tables rather than Python subclasses. | Standard relational translation; Python duck-typing means the subclass layout adds no runtime value. Kept as inheritance on the diagram for submission. |
| `early_termination()` returns a dict, not a scalar. | Sprint 3 added the 1-month notice period. Returning `{"penalty", "effective_date"}` is cleaner than returning a tuple and easier to extend. |
| PDF generation is a dedicated module (`views/pdf_generator.py`) rather than a method on `Invoice`. | Brief asks for a "PDF or text bill." The PDF path is a late (Sprint 4) addition using `fpdf2`; putting it on `Invoice` would couple a data row to a rendering library. |
| Design tokens + UI helpers (`theme.py`, `ui_helpers.py`) added as a utility layer. | Sprint 4 UI redesign — removed hardcoded colors/fonts from every view and replaced `messagebox.*` calls with a dark-theme toast + confirm dialog pair. |
