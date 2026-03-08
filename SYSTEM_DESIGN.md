# System Design Specifications (Final Universal Notation)

This document is the **Gold Standard** for your Astah Diagram.
**Notation Rules Used:**
*   `int` (not Integer)
*   `double` (not Float/Decimal, for currency)
*   `boolean` (not Boolean)
*   `String` (Standard text type)
*   `List<Type>` (for collections)

---

## 1. Class Definitions

### 1.1 Core System
**Class: `AuthManager`** (Previously PAMSController)

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- current_user : User` | **Type `User`**: Stores the currently logged-in object. |
| **Operations** | |
| `+ login(username: String, password: String) : boolean` | **Type `boolean`**: Returns `true` on success, `false` on failure. |
| `+ logout() : void` | **Type `void`**: No return value. |
| `+ create_user(user: String, pass: String, role: String, empID: String, dept: String) : boolean` | **Type `boolean`**: Handles transactional creation of users + staff. |
| `+ get_dashboard_stats() : Map<String, int>` | **Type `Map<String, int>`**: Returns stats like `{"Open Tickets": 5}`. |

---

### 1.2 User Hierarchy
**Parent Class: `User`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- id : int` | **Type `int`**: Unique database ID. |
| `- username : String` | **Type `String`**: Login name. |
| `- password_hash : String` | **Type `String`**: Encrypted password. |
| `- role : String` | **Type `String`**: "Admin", "Staff", or "Tenant". |
| `- created_at : DateTime` | **Type `DateTime`**: Audit timestamp. |
| `- last_login : DateTime` | **Type `DateTime`**: Activity tracking. |
| **Operations** | |
| `+ check_password(input: String) : boolean` | **Type `boolean`**: Verifies password. |
| `+ update_profile(data: Map<String, String>) : boolean` | **Type `boolean`**: Returns `true` if update succeeded. |

**Child Class: `Admin`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | *(Inherits from User)* |
| **Operations** | |
| `+ create_user(u: User) : int` | **Type `int`**: Returns the new User ID. |
| `+ delete_user(id: int) : boolean` | **Type `boolean`**: Returns `true` if deleted. |
| `+ backup_system() : File` | **Type `File`**: Returns the backup file object. |

**Child Class: `Staff`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- employee_id : String` | **Type `String`**: Company ID (e.g. "EMP001"). |
| `- department : String` | **Type `String`**: Work area. |
| **Operations** | |
| `+ view_assigned_tickets() : List<MaintenanceRequest>` | **Type `List`**: Returns a list of strictly typed request objects. |

**Child Class: `Tenant`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- full_name : String` | **Type `String`**: Legal name. |
| `- email : String` | **Type `String`**: Contact email. |
| `- phone_number : String` | **Type `String`**: Text format for phones. |
| `- emergency_contact : String` | **Type `String`**: Emergency info. |
| `- lease_start_date : Date` | **Type `Date`**: Lease start (Time irrelevant). |
| `- lease_end_date : Date` | **Type `Date`**: Lease end (Time irrelevant). |
| **Operations** | |
| `+ get_outstanding_balance() : double` | **Type `double`**: Returns exact monetary debt. |
| `+ request_maintenance(desc: String) : MaintenanceRequest` | **Type `MaintenanceRequest`**: Returns the created ticket. |

---

### 1.3 Property Management
**Class: `Apartment`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- id : int` | **Type `int`**: Unique ID. |
| `- unit_number : String` | **Type `String`**: Supports "4B", "PH". |
| `- address : String` | **Type `String`**: Physical address. |
| `- rental_price : double` | **Type `double`**: Monthly rent price. |
| `- square_footage : int` | **Type `int`**: Size in sq ft. |
| `- status : String` | **Type `String`**: "Occupied", "Vacant". |
| **Operations** | |
| `+ assign_tenant(t: Tenant) : boolean` | **Type `boolean`**: Returns `true` if assignment worked. |
| `+ vacate() : boolean` | **Type `boolean`**: Returns `true` if processed. |

---

### 1.4 Finance Module
**Class: `Invoice`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- id : int` | **Type `int`**: Unique ID. |
| `- issue_date : Date` | **Type `Date`**: Billing date. |
| `- due_date : Date` | **Type `Date`**: Payment deadline. |
| `- total_amount : double` | **Type `double`**: Bill total. |
| `- status : String` | **Type `String`**: "Paid", "Pending". |
| **Operations** | |
| `+ calculate_balance() : double` | **Type `double`**: Remaining amount to pay. |
| `+ generate_pdf() : File` | **Type `File`**: PDF document. |
| `+ add_payment(p: Payment) : void` | **Type `void`**: Just links the payment. |

**Class: `Payment`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- id : int` | **Type `int`**: Unique ID. |
| `- amount : double` | **Type `double`**: Amount paid. |
| `- payment_date : DateTime` | **Type `DateTime`**: Exact timestamp of transfer. |
| `- method : String` | **Type `String`**: "Card", "Cash". |
| `- transaction_ref : String` | **Type `String`**: Bank Receipt ID. |
| **Operations** | |
| `+ verify_status() : boolean` | **Type `boolean`**: valid/invalid check. |

---

### 1.5 Operations Module
**Class: `MaintenanceRequest`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- id : int` | **Type `int`**: Unique ID. |
| `- date_reported : DateTime` | **Type `DateTime`**: Submission time. |
| `- description : String` | **Type `String`**: Issue details. |
| `- priority : String` | **Type `String`**: "High", "Low". |
| `- status : String` | **Type `String`**: "Open", "Fixed". |
| `- date_resolved : DateTime` | **Type `DateTime`**: Completion time (Nullable). |
| **Operations** | |
| `+ update_status(new_status: String) : void` | **Type `void`**: Updates status string. |
| `+ assign_staff(s: Staff) : void` | **Type `void`**: Assigns worker. |

---

### 1.6 UI Boundary Classes (New)
**Class: `UserView`**

| **Specs for Astah** | **Detailed Explanation** |
| :--- | :--- |
| **Attributes** | |
| `- entry_username : Entry` | **Type `Entry`**: Input field. |
| `- entry_password : Entry` | **Type `Entry`**: Input field (Masked). |
| `- entry_empid : Entry` | **Type `Entry`**: **NEW** (Hidden for non-staff). |
| `- entry_dept : Entry` | **Type `Entry`**: **NEW** (Hidden for non-staff). |
| **Operations** | |
| `+ toggle_staff_fields() : void` | **Type `void`**: Shows/Hides inputs based on Role dropdown. |
| `+ create_user() : void` | **Type `void`**: Triggered by Button Click. |

---

## 2. Relationships (Quick Reference)

| **Source** | **Target** | **Line Type** | **Logic** |
| :--- | :--- | :--- | :--- |
| **Admin** / **Staff** / **Tenant** | **User** | **Inheritance** (White Triangle) | "Is A" User |
| **AuthManager** | **User** | **Dependency** (Dashed Arrow) | Controller "Uses" User |
| **Apartment** (1) | **Tenant** (0..1) | **Association** (Solid Line) | Occupancy |
| **Apartment** (1) | **MaintenanceRequest** (*) | **Association** (Solid Line) | Property History |
| **Tenant** (1) | **Invoice** (*) | **Association** (Solid Line) | Billing History |
| **Invoice** (Diamond) | **Payment** (*) | **Composition** (Solid Diamond) | Financial Integrity |
