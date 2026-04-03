# 🧪 Sprint 1 Master Test Plan — PAMS Group 28
**Sprint:** 1 | **Branch:** `dev` | **Review Date:** 6 Apr 2026

---

## 🏗️ Pre-Requisites (Setup for Testing)

Before running these tests, completely reset the environment so we all test from the exact same baseline data.

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

---

## 🔐 1. Authentication & Role Access (Omar)

**Tester:** Anyone

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| AUTH-01 | Run app | Login screen appears with Modern UI | ⬜ |
| AUTH-02 | Login with `admin` / `admin123` | Lands on Dashboard, ALL sidebar tabs visible | ⬜ |
| AUTH-03 | Logout and login as `frontdesk1` / `pass123` | Sidebar shows ONLY Dashboard and Tenants. Others hidden. | ⬜ |
| AUTH-04 | Logout and login as `finance1` / `pass123` | Sidebar shows ONLY Dashboard and Finance. Others hidden. | ⬜ |
| AUTH-05 | Logout and login as `maint1` / `pass123` | Sidebar shows ONLY Dashboard and Maintenance. | ⬜ |
| AUTH-06 | Logout and login as `manager1` / `pass123` | Sidebar shows ONLY Dashboard and Reports. | ⬜ |
| AUTH-07 | Try invalid password `admin` / `wrong` | Error popup: "Invalid username or password" | ⬜ |

---

## 👤 2. Tenant Management (Feras)

**Tester:** Focus on Front Desk role (Login: `frontdesk1` / `pass123`)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| TEN-01 | Go to Tenants → Active Tenants | Should see 2 existing seeded tenants (John Smith, Sarah Jones) | ⬜ |
| TEN-02 | Go to Register Tab. Leave "NI Number" blank, click Submit | Warning popup: "NI, Name, Username, Password are required" | ⬜ |
| TEN-03 | Register valid tenant "Mike Ross", NI: 999111, Pass: 123 | Success popup, fields clear, Mike appears in Active Tenants | ⬜ |
| TEN-04 | Go to Actions Tab. Enter nonexistent Tenant ID (999) | Error popup: "Tenant not found" | ⬜ |
| TEN-05 | Early terminate Tenant ID 6 (John Smith) | Success popup showing £42.50 penalty (5% of 850) | ⬜ |
| TEN-06 | Check Active Tenants list after TEN-05 | John Smith is no longer in the list | ⬜ |
| TEN-07 | Log in as `admin`, check 'Apartments' tab | Apartment 101 (formerly John's) should now say "Vacant" | ⬜ |
| TEN-08 | Dashboard (as admin) | Total tenants should be updated | ⬜ |

---

## 💷 3. Financial Module (Ahmed)

**Tester:** Focus on Finance role (Login: `finance1` / `pass123`)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| FIN-01 | Go to Finance → Generate Invoice. ID: 7, Amount: blank | Generates invoice for Sarah based on her £1100 rent | ⬜ |
| FIN-02 | Check All Invoices Tab | Shows new invoice. Status: Pending. Due date: today + 30 days | ⬜ |
| FIN-03 | Generate Invoice. ID: 999 (Invalid) | Error popup: "Tenant not found" | ⬜ |
| FIN-04 | Payment Processing → Record Payment. Invoice: 1, Amt: 850 | Success popup | ⬜ |
| FIN-05 | Check All Invoices Tab after FIN-04 | Invoice 1 status changes from "Pending" to "Paid" | ⬜ |
| FIN-06 | Record Payment. Invoice: 1, Amt: 100 | Error popup: "Invoice already paid" | ⬜ |
| FIN-07 | Overdue Tab | Verify empty (no invoices are 30 days old yet) | ⬜ |
| FIN-08 | Generate manual invoice ID: 7, Amount: £500 | Success, appears as Pending | ⬜ |

---

## 🔧 4. Maintenance Module (Numair)

**Tester:** Focus on Maintenance role (Login: `maint1` / `pass123`)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| MNT-01 | Maintenance → Manage Tab. Try updating wrong ID | Error popup: "Ticket not found" (or similar) | ⬜ |
| MNT-02 | New Ticket Tab. Apt: 201, Desc: Fix sink, Urgent | Success popup, fields clear | ⬜ |
| MNT-03 | All Tickets Tab | Shows new ticket. Status: Open. Priority: Urgent. | ⬜ |
| MNT-04 | Manage Tab. Assign staff ID 5 (Mike) to new ticket | Success popup | ⬜ |
| MNT-05 | All Tickets Tab | Ticket now shows "Assigned To: maint1" and Status: "Assigned" | ⬜ |
| MNT-06 | Manage Tab. Update Status to "In Progress" | Success popup | ⬜ |
| MNT-07 | Manage Tab. Log costs: 2.5 hours, £150 cost | Success popup | ⬜ |
| MNT-08 | All Tickets Tab | Highlights updated status/costs | ⬜ |
| MNT-09 | Manage Tab. Update Status to "Fixed" | Success, date resolved is recorded in DB | ⬜ |

---

## 🚀 5. End-to-End System Integrity (All)

**Tester:** Admin (`admin` / `admin123`)

| Test ID | Action | Expected Result | Pass/Fail |
|---------|--------|-----------------|-----------|
| E2E-01 | Check Dashboard Stats | Matches actions done above (e.g. 1 tenant left, new maintenance tickets) | ⬜ |
| E2E-02 | Add totally new Apartment | Success | ⬜ |
| E2E-03 | Add new Staff member | Success | ⬜ |
| E2E-04 | Click through every single tab | App does not crash. No Python exceptions in terminal. | ⬜ |

---

## 🚨 Bug Reporting Protocol

If any test fails (⬜ becomes ❌):
1. **Take a screenshot** of the error / crash.
2. Note the **Test ID** (e.g., `MNT-04`).
3. Message the group chat / Omar immediately.
4. DO NOT attempt to write quick fixes directly to `dev`. Create a hotfix branch (e.g. `feature/fix-mnt-04`) and PR it.
