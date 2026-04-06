# 🧪 Sprint 2 Master Test Plan — PAMS Group 28
**Sprint:** 2 | **Branch:** `dev` | **Review Date:** 6 Apr 2026

---

## 🏗️ Pre-Requisites (Setup for Testing)

Every tester must start from the exact same baseline. Run this before starting **any** section:

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
source venv/bin/activate
pip install -r requirements.txt
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py
```

**Automated tests first** — confirm all 133 pass before any manual testing:
```bash
python3 -m unittest discover -s tests -v
```
Expected output: `Ran 133 tests in ~10s` — `OK`

---

### Seeded Test Data Reference

| Login | Role | Password | Tabs visible |
|-------|------|----------|--------------|
| admin | admin | admin123 | All |
| frontdesk1 | front_desk | pass123 | Dashboard, Tenants |
| finance1 | finance_manager | pass123 | Dashboard, Invoices, Payments |
| maint1 | maintenance | pass123 | Dashboard, Maintenance |
| manager1 | manager | pass123 | Dashboard, Reports |

| Tenant | User ID | Apartment | City | Rent | Status |
|--------|---------|-----------|------|------|--------|
| John Smith | 6 | 101 (Bristol) | Bristol | £850 | Active |
| Sarah Jones | 7 | 201 (Cardiff) | Cardiff | £1100 | Active |

| Invoice | Tenant | Amount | Status | Notes |
|---------|--------|--------|--------|-------|
| 1 | John | £850 | Pending | **OVERDUE** (due 5 days ago) |
| 2 | John | £850 | Pending | Due in 25 days |
| 3 | Sarah | £1100 | Paid | Paid via Bank Transfer |
| 4 | Sarah | £1100 | Pending | Due in 25 days |

| Ticket | Apartment | Tenant | Description | Priority | Status |
|--------|-----------|--------|-------------|----------|--------|
| 1 | 101 Bristol | John | Leaking kitchen tap | High | Fixed |
| 2 | 201 Cardiff | Sarah | Broken window latch | Medium | Fixed |
| 3 | 101 Bristol | John | Flickering hallway light | Low | Open |

---

## 🔐 1. Authentication & Role Access

**Tester:** Anyone | **Login:** various

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| AUTH-01 | Launch app | Login screen appears, no crash | ⬜ |
| AUTH-02 | Login `admin` / `admin123` | Lands on Dashboard. Sidebar shows: Dashboard, Tenants, Invoices, Payments, Maintenance, Reports, Users | ⬜ |
| AUTH-03 | Logout → login `frontdesk1` / `pass123` | Sidebar shows ONLY: Dashboard, Tenants. No Invoices, Payments, Maintenance, Reports | ⬜ |
| AUTH-04 | Logout → login `finance1` / `pass123` | Sidebar shows ONLY: Dashboard, Invoices, Payments | ⬜ |
| AUTH-05 | Logout → login `maint1` / `pass123` | Sidebar shows ONLY: Dashboard, Maintenance | ⬜ |
| AUTH-06 | Logout → login `manager1` / `pass123` | Sidebar shows ONLY: Dashboard, Reports | ⬜ |
| AUTH-07 | Wrong password: `admin` / `wrongpass` | Error popup: "Invalid username or password" | ⬜ |
| AUTH-08 | Wrong username: `nobody` / `admin123` | Error popup: "Invalid username or password" | ⬜ |
| AUTH-09 | Empty fields, click Login | Warning or error shown — does not crash | ⬜ |

---

## 👤 2. Tenant Management — Sprint 2 Features (Feras)

**Tester:** Login as `frontdesk1` / `pass123`, go to Tenants tab

### 2a. Search & Filter

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| TEN-01 | Open Active Tenants tab | John Smith and Sarah Jones both visible. Status filter set to "Active" | ⬜ |
| TEN-02 | Summary bar at top of Active Tenants | Shows count labels: "Active: 2" at minimum | ⬜ |
| TEN-03 | Type "john" in search box | List filters live — only John Smith visible | ⬜ |
| TEN-04 | Type "sarah@email.com" in search box | Only Sarah Jones visible (email match) | ⬜ |
| TEN-05 | Type "07712345678" in search box | Only John Smith visible (phone match) | ⬜ |
| TEN-06 | Type "NI123456A" in search box | Only John Smith visible (NI match) | ⬜ |
| TEN-07 | Type "zzznomatch" in search box | List is empty — no results | ⬜ |
| TEN-08 | Click 🔄 Reset button | Search cleared, all Active tenants shown again | ⬜ |
| TEN-09 | Status filter → "All" | Both tenants appear (no Archived/Terminated yet, so same 2) | ⬜ |

### 2b. Register & Actions

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| TEN-10 | Register Tab — leave NI blank, click Register | Warning: required fields message | ⬜ |
| TEN-11 | Register valid tenant: NI: AB999999Z, Name: Mike Ross, Username: mikeross, Pass: pass123 | Success popup, Mike appears in Active Tenants | ⬜ |
| TEN-12 | Summary bar after TEN-11 | "Active" count increments to 3 | ⬜ |
| TEN-13 | Actions Tab — enter non-existent ID (9999), click Early Termination | Error: "Tenant not found" | ⬜ |
| TEN-14 | Actions Tab — enter ID 6 (John), click Early Termination → confirm | Success popup showing penalty £42.50 (5% of £850) | ⬜ |
| TEN-15 | Active Tenants after TEN-14 | John Smith gone from Active list | ⬜ |
| TEN-16 | Archived/Terminated tab after TEN-14 | John Smith appears with status "Terminated" | ⬜ |
| TEN-17 | Login as `admin`, Apartments tab | Apartment 101 (Bristol) now shows "Vacant" | ⬜ |
| TEN-18 | Login as `admin`, Actions Tab — enter ID 6, click Early Termination again | Error: "Tenant is already Terminated" | ⬜ |
| TEN-19 | Login as `admin`, Actions Tab — Archive Tenant ID 7 (Sarah) → confirm | Success: Sarah archived | ⬜ |
| TEN-20 | Archived/Terminated tab after TEN-19 | Shows both John (Terminated) and Sarah (Archived) | ⬜ |
| TEN-21 | Click Tenants tab freshly after all above actions | Tab loads without crash — no `archived_tree` AttributeError | ⬜ |

---

## 💰 3. Invoice Management — Sprint 2 Features (Ahmed)

**Tester:** Login as `finance1` / `pass123`, go to Invoices tab

### 3a. All Invoices with Overdue Badge

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| INV-01 | Open All Invoices tab | 4 invoices visible. Invoice 1 shows "⚠️ OVERDUE" in status column | ⬜ |
| INV-02 | Invoice 3 status column | Shows "Paid" (no overdue badge — already paid) | ⬜ |
| INV-03 | Invoice 2 and 4 status column | Both show "Pending" (not overdue — due in future) | ⬜ |
| INV-04 | All amounts shown with £ symbol | e.g. "£850.00", "£1100.00" — not raw numbers | ⬜ |

### 3b. Generate Invoice

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| INV-05 | Generate Invoice — Tenant ID: 7, Amount: blank | Success popup. New invoice for £1100 (Sarah's monthly rent) | ⬜ |
| INV-06 | Generate Invoice — Tenant ID: 999 | Error: "Tenant not found" | ⬜ |
| INV-07 | Generate Invoice — Tenant ID: 7, Amount: -500 | Error: "Invalid amount" | ⬜ |
| INV-08 | Generate Invoice — Amount: "abc" | Error: "must be valid numbers" | ⬜ |

### 3c. Overdue Tab

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| INV-09 | Open Overdue tab | Invoice 1 (John, £850) appears. Invoice 3 (Paid) does NOT appear | ⬜ |
| INV-10 | Overdue tab columns | ID, Tenant, Due Date, Amount columns all have headings | ⬜ |

### 3d. Late Payment Notifications Tab

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| INV-11 | Open Late Notifications tab | Invoice 1 for John Smith appears with contact info | ⬜ |
| INV-12 | Late Notifications — column headings | Invoice, Tenant, Email, Phone, Due Date, Amount, Days Overdue all visible | ⬜ |
| INV-13 | "Days Overdue" column for Invoice 1 | Shows "5 days" (approximately — due 5 days ago) | ⬜ |
| INV-14 | Email column for John | Shows "john@email.com" | ⬜ |
| INV-15 | Phone column for John | Shows "07712345678" | ⬜ |
| INV-16 | Invoice 3 (Sarah, Paid) | Does NOT appear in Late Notifications | ⬜ |

---

## 💳 4. Payment Management — Sprint 2 Features (Ahmed)

**Tester:** Login as `finance1` / `pass123`, go to Payments tab

### 4a. Record Payment

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| PAY-01 | Record Payment — Invoice: 1, Amount: 850, Method: Card | Success popup, invoice 1 status becomes Paid | ⬜ |
| PAY-02 | Record Payment on Invoice 1 again | Error: "Invoice already paid" | ⬜ |
| PAY-03 | Record Payment — Invoice: 1, Amount: -100 | Error: "Amount must be positive" | ⬜ |
| PAY-04 | Record Payment — Invoice: 999 | Error: "Invoice not found" | ⬜ |
| PAY-05 | Record Payment — Invoice: 2, Amount: 9999 | Error: "Amount exceeds remaining balance" | ⬜ |
| PAY-06 | Payment History tab after PAY-01 | Shows new payment row for John, £850.00, Card | ⬜ |

### 4b. Financial Summary Tab

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| PAY-07 | Open Financial Summary tab | 3 summary cards visible: Collected, Pending, Total Invoiced | ⬜ |
| PAY-08 | Collected card (before PAY-01) | Shows £1100.00 (only Sarah's Bank Transfer payment seeded) | ⬜ |
| PAY-09 | Pending card (before PAY-01) | Shows £1700.00 (Invoice 1 £850 + Invoice 2 £850 — Invoice 4 is Pending too making it £2950 total pending) | ⬜ |
| PAY-10 | After PAY-01 — Collected card | Updates to £1950.00 (£1100 + £850) | ⬜ |
| PAY-11 | Payment Method Breakdown table | Shows at least "Bank Transfer" row from seeded data. Headings: Payment Method, Total Amount, Transaction Count | ⬜ |
| PAY-12 | After PAY-01 — Method table | "Card" row appears with £850.00, count 1 | ⬜ |
| PAY-13 | Monthly Revenue table | Shows current month row after PAY-01 with £850.00 | ⬜ |
| PAY-14 | Monthly Revenue heading | "Monthly Revenue (Last 6 Months)" label visible above table | ⬜ |

---

## 🔧 5. Maintenance Management — Sprint 2 Features (Numair)

**Tester:** Login as `maint1` / `pass123`, go to Maintenance tab

### 5a. Existing Functionality (regression)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| MNT-01 | All Tickets tab | 3 seeded tickets visible. Ticket 1 & 2: Fixed. Ticket 3: Open | ⬜ |
| MNT-02 | Ticket list sorted correctly | Urgent/High before Medium/Low — Ticket 1 (High) before Ticket 3 (Low) | ⬜ |
| MNT-03 | New Ticket — Apt: 1, Desc: "Fix sink", Priority: Urgent | Success popup, ticket appears in list as Open | ⬜ |
| MNT-04 | New Ticket — leave description blank | Error: "Apartment ID and description required" | ⬜ |
| MNT-05 | New Ticket — Apt: 9999 | Error: "Apartment not found" | ⬜ |

### 5b. Notify Tenant (Manage Tab)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| MNT-06 | Manage tab — Ticket ID: 3, Date: 2026-04-15, click Set Date & Notify | Success popup showing: "Tenant: John Smith", "Phone: 07712345678", "Email: john@email.com" | ⬜ |
| MNT-07 | After MNT-06 — All Tickets tab | Ticket 3 now shows scheduled date | ⬜ |
| MNT-08 | Notify Tenant — Ticket ID: 9999 | Error: "Ticket not found" | ⬜ |
| MNT-09 | Notify Tenant — leave date blank | Warning: "Ticket ID and date required" | ⬜ |
| MNT-10 | Notify new ticket (no tenant linked, from MNT-03) | Popup shows: "Tenant: No tenant linked" — does not crash | ⬜ |

### 5c. Cost Report Tab

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| MNT-11 | Open Cost Report tab | Tab loads without crash. Summary cards visible | ⬜ |
| MNT-12 | Summary cards on Cost Report | "Total Tickets: 3", "Fixed: 2", "Open: 1" (or Urgent:1 after MNT-03) | ⬜ |
| MNT-13 | Cost by Apartment table | Unit 101 (Bristol) row shows: 2 tickets, £150.00 total cost, 2.5h | ⬜ |
| MNT-14 | Cost by Apartment — Unit 201 row | Cardiff, 1 ticket, £75.00, 1.0h | ⬜ |
| MNT-15 | Cost by Apartment sorted | 101 (£150) appears above 201 (£75) — sorted by cost DESC | ⬜ |
| MNT-16 | Cost by City table | Bristol row: 2 tickets, £150.00. Cardiff row: 1 ticket, £75.00 | ⬜ |
| MNT-17 | Click 🔄 Refresh Report button | Tables reload, no crash | ⬜ |
| MNT-18 | Column headings in both tables | Unit, City, Total Tickets, Open, Resolved, Total Cost, Total Hours, Avg Cost all visible | ⬜ |
| MNT-19 | After logging costs on new ticket (Assign + log £200, 3h to MNT-03 ticket) | Apt 101 total cost updates to £350, Bristol city total updates | ⬜ |

### 5d. Status Update + Cost Logging (regression)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| MNT-20 | Manage Tab — Ticket ID: 3, Status: "Fixed" (invalid — skip In Progress) | Error: "Cannot transition from 'Open' to 'Fixed'" | ⬜ |
| MNT-21 | Manage Tab — Ticket ID: 3, Status: "In Progress" | Status updated, manage_result label confirms | ⬜ |
| MNT-22 | Log costs on Ticket 3: 1.5h, £60 | Success — costs accumulate | ⬜ |

---

## 📊 6. Reports Module (Omar)

**Tester:** Login as `manager1` / `pass123`, go to Reports tab

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| RPT-01 | Open Reports tab | Occupancy Report tab loads, data visible, no crash | ⬜ |
| RPT-02 | Occupancy Report — filter "All Cities" | All 5 apartments shown across Bristol, Cardiff, London, Manchester | ⬜ |
| RPT-03 | Occupancy Report — filter "Bristol" | Shows only 101 (Occupied) and 102 (Vacant) | ⬜ |
| RPT-04 | Occupancy summary cards for Bristol | "Total: 2", "Occupied: 1", "Vacant: 1", "Occupancy Rate: 50%" | ⬜ |
| RPT-05 | Financial Summary tab | Shows Collected vs Pending totals matching payment data | ⬜ |
| RPT-06 | Maintenance Cost Report tab | Shows cost data per apartment and city matching seeded data | ⬜ |
| RPT-07 | Maintenance Cost — Bristol | Shows £150.00 total, 2 tickets | ⬜ |

---

## 🔔 7. Notification Badge (Omar)

**Tester:** Login as `admin` / `admin123`

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| NOTIF-01 | Header area after login | Notification badge visible (e.g. 🔔 or count) — 1 overdue invoice seeded | ⬜ |
| NOTIF-02 | Click notification badge / bell | Notification panel opens showing overdue invoice for John | ⬜ |
| NOTIF-03 | Expiring lease notification | John's lease ended 2026-01-01 — should appear in expiry warnings (past due) | ⬜ |

---

## 🏠 8. Apartment & User Management (Omar / Admin)

**Tester:** Login as `admin` / `admin123`

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| APT-01 | Apartments tab | All 5 seeded apartments visible with correct status | ⬜ |
| APT-02 | Add apartment — Unit: 501, Address: 9 Test Rd, City: Leeds, Rooms: 2, Price: 700, SqFt: 500 | Success, appears in list as Vacant | ⬜ |
| APT-03 | Add apartment — missing required fields | Error shown — does not crash | ⬜ |
| USR-01 | Users tab | All 7 seeded users visible | ⬜ |
| USR-02 | Create new staff: username "newstaff", role "maintenance" | Success popup | ⬜ |

---

## 🔁 9. End-to-End Flow

**Tester:** Login as `admin` / `admin123`. Run this as one continuous flow.

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| E2E-01 | Register new tenant: NI: CD111111D, Name: Alice Brown, Username: alice, Pass: pass123 | Success | ⬜ |
| E2E-02 | Assign Alice to Apartment 102 (Vacant, Bristol): Lease 2026-04-06 → 2027-04-06, Rent: £600, Deposit: £600 | Success — Apt 102 changes to Occupied | ⬜ |
| E2E-03 | Finance: Generate invoice for Alice (Tenant ID from list), Amount: blank | Invoice created for £600 | ⬜ |
| E2E-04 | Payments: Pay Alice's invoice, £600, Bank Transfer | Invoice marked Paid | ⬜ |
| E2E-05 | Financial Summary — Collected card | Increased by £600 | ⬜ |
| E2E-06 | Maintenance: New ticket for Apt 102, Desc: "Damp wall", Priority: High | Success | ⬜ |
| E2E-07 | Maintenance: Assign maint1 (user ID 4) to new ticket | Status → Assigned | ⬜ |
| E2E-08 | Maintenance: Notify Tenant on new ticket with date 2026-04-20 | Popup shows Alice's contact info | ⬜ |
| E2E-09 | Cost Report — Apt 102 row | Appears with 1 ticket, £0 cost (not logged yet) | ⬜ |
| E2E-10 | Archive Alice (Actions Tab) | Success. Apt 102 → Vacant | ⬜ |
| E2E-11 | Try to generate invoice for Alice after E2E-10 | Error: "Cannot invoice a Archived tenant" | ⬜ |
| E2E-12 | Click through ALL tabs in order | No crashes, no Python exceptions in terminal | ⬜ |

---

## ⚡ 10. Edge Cases & Security

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| SEC-01 | Payment — Invoice: 2, Amount: 0 | Error: "Amount must be positive" | ⬜ |
| SEC-02 | Maintenance cost log — negative values | Error: "Time and cost must be positive" | ⬜ |
| SEC-03 | Assign apartment to Terminated tenant (ID 6 after TEN-14) | Error: "Cannot assign apartment to a Terminated tenant" | ⬜ |
| SEC-04 | Archive an already-Archived tenant | Error: "Tenant is already Archived" | ⬜ |
| SEC-05 | Try paying a Paid invoice (Invoice 3) | Error: "Invoice already paid" | ⬜ |
| SEC-06 | Record overpayment — Invoice 2 has £850 due, try paying £9999 | Error: "Amount exceeds remaining balance" | ⬜ |
| SEC-07 | Maintenance status transition — Closed → In Progress | Error: "Cannot transition from 'Closed' to 'In Progress'" | ⬜ |

---

## 🤖 11. Automated Test Suite Summary

Run at the end to confirm nothing was broken by manual testing (particularly if `pams.db` was modified):

```bash
rm -f pams.db
python3 -m unittest discover -s tests -v 2>&1 | tail -5
```

| Module | Test File | Count | Pass/Fail |
|--------|-----------|-------|-----------|
| Auth + Property | test_auth_manager, test_property_manager | 17 | ⬜ |
| Tenant | test_tenant_manager | 4 | ⬜ |
| Finance | test_finance | ~12 | ⬜ |
| Maintenance Sprint 1 | test_maintenance | 7 | ⬜ |
| Reports + Notifications | test_reports_notifications | 21 | ⬜ |
| Ahmed Sprint 2 | test_ahmed_sprint2 | 39 | ⬜ |
| Numair Sprint 2 | test_numair_sprint2 | 40 | ⬜ |
| **Total** | | **133** | ⬜ |

---

## 🚨 Bug Reporting Protocol

If any test fails (⬜ becomes ❌):
1. Take a **screenshot** of the error / terminal output.
2. Note the **Test ID** (e.g. `MNT-13`).
3. Message Omar immediately — do **not** push fixes directly to `dev`.
4. Create a hotfix branch: `git checkout -b hotfix/<test-id>` and open a PR.
