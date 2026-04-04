# 🚀 Sprint 2 Git Guide — PAMS Group 28
**Last updated:** 3 Apr 2026 | **Branch strategy:** `feature/*` → `dev` → `main` | **Repo:** `OmarFrouh/ASD-UWE-2026`

---

## Progress Tracker

| Step | Target Date | Task | Owner | Status |
|:-----|:------------|:-----|:------|:-------|
| 0 | 7 Apr | Push Sprint 2 foundation (report skeleton + notification system) to `dev` | Omar | ✅ DONE |
| 1 | 7 Apr | Pull `dev`, create `feature/tenant-sprint2`, start coding | Feras | ✅ DONE |
| 2 | 7 Apr | Pull `dev`, create `feature/finance-sprint2`, start coding | Ahmed | ⬜ TODO |
| 3 | 7 Apr | Pull `dev`, create `feature/maintenance-sprint2`, start coding | Numair | ⬜ TODO |
| 4 | 10 Apr | Push `feature/tenant-sprint2` + PR to `dev` | Feras | ✅ DONE |
| 5 | 10 Apr | Push `feature/finance-sprint2` + PR to `dev` | Ahmed | ⬜ TODO |
| 6 | 10 Apr | Push `feature/maintenance-sprint2` + PR to `dev` | Numair | ⬜ TODO |
| 7 | 11 Apr | Review + merge all 3 PRs into `dev` | Omar | ⬜ TODO |
| 8 | 11 Apr | Everyone pulls updated `dev`, confirms app still runs | ALL | ⬜ TODO |
| 9 | 13 Apr | Sprint 2 review meeting | ALL | ⬜ TODO |
| 10 | 13 Apr | Merge `dev` → `main` (Sprint 2 complete snapshot) | Omar | ⬜ TODO |

---

## File Ownership — Sprint 2

> Same ownership as Sprint 1 + new files listed below for each member.

| File | Owner | Sprint 2 Action |
|:-----|:------|:----------------|
| `views/report_view.py` | Omar | **[NEW]** Create |
| `report_manager.py` | Omar | **[NEW]** Create |
| `notification_manager.py` | Omar | **[NEW]** Create |
| `views/main_view.py` | Omar | MODIFY (wire reports view + notification badge) |
| `seed_db.py` | Omar | MODIFY (add overdue invoice data for testing) |
| `views/tenant_view.py` | Feras | MODIFY (add search/filter, notification display) |
| `tenant_manager.py` | Feras | MODIFY (add search/filter queries) |
| `views/invoice_view.py` | Ahmed | MODIFY (add late payment badges, notification triggers) |
| `views/payment_view.py` | Ahmed | MODIFY (add financial summary tab) |
| `invoice_manager.py` | Ahmed | MODIFY (add overdue notification logic) |
| `payment_manager.py` | Ahmed | MODIFY (add financial summary queries) |
| `views/maintenance_view.py` | Numair | MODIFY (add cost summary tab, date communication) |
| `maintenance_manager.py` | Numair | MODIFY (add cost report queries, date notification) |
| `tests/` | Everyone | Add Sprint 2 test cases to your existing test files |

---

## STEP 0 — Omar: Push Sprint 2 Foundation to `dev`

**Who:** Omar

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
source venv/bin/activate

# Create the new files (see guides/sprint2/SPRINT2_OMAR.md for full code)
# Then:
git add report_manager.py notification_manager.py views/report_view.py seed_db.py views/main_view.py
git commit -m "Sprint 2 (Omar): Report skeleton, notification manager, updated seed data"
git push origin dev

# Message the team: "Sprint 2 foundation pushed. Pull from dev and start your branches!"
```

---

## STEP 1 — Feras: Setup + Tenant Search/Filter

**Who:** Feras

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/tenant-sprint2
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads with: admin / admin123
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/tenant-sprint2 && git merge dev`

**Your files to modify** (from `guides/sprint2/SPRINT2_FERAS.md`):
- `tenant_manager.py` — add `search_tenants()` and `filter_tenants_by_status()` methods
- `views/tenant_view.py` — add search bar, status filter dropdown, notification display

```bash
# After coding:
git add tenant_manager.py views/tenant_view.py
git commit -m "Sprint 2 (Feras): tenant search, filter, notification display"
git push origin feature/tenant-sprint2
```

---

## STEP 2 — Ahmed: Setup + Financial Summary + Late Payment Notifications

**Who:** Ahmed

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/finance-sprint2
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/finance-sprint2 && git merge dev`

**Your files to modify** (from `guides/sprint2/SPRINT2_AHMED.md`):
- `invoice_manager.py` — add `get_overdue_with_details()` method
- `payment_manager.py` — add `get_collected_vs_pending()` method
- `views/invoice_view.py` — add visual overdue badges
- `views/payment_view.py` — add "Financial Summary" tab

```bash
# After coding:
git add invoice_manager.py payment_manager.py views/invoice_view.py views/payment_view.py
git commit -m "Sprint 2 (Ahmed): financial summary, late payment notification, overdue badges"
git push origin feature/finance-sprint2
```

---

## STEP 3 — Numair: Setup + Maintenance Cost Report + Date Communication

**Who:** Numair

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/maintenance-sprint2
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/maintenance-sprint2 && git merge dev`

**Your files to modify** (from `guides/sprint2/SPRINT2_NUMAIR.md`):
- `maintenance_manager.py` — add `get_cost_report_by_apartment()`, `get_cost_report_by_city()`, `notify_tenant_scheduled_date()`
- `views/maintenance_view.py` — add "Cost Report" tab, "Notify Tenant" button

```bash
# After coding:
git add maintenance_manager.py views/maintenance_view.py
git commit -m "Sprint 2 (Numair): maintenance cost reports, date communication, tenant notification"
git push origin feature/maintenance-sprint2
```

---

## STEP 4 — Feras: Open Pull Request

**Who:** Feras

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. You'll see a yellow banner: **"Compare & pull request"** for `feature/tenant-sprint2`
3. Click it
4. Set **base: `dev`** ← **compare: `feature/tenant-sprint2`**
5. Title: `Sprint 2 (Feras): Tenant search, filter, and notification display`
6. Description: List what you built (search bar, status filter, notification display)
7. Assign **Omar** as reviewer (right sidebar → "Reviewers")
8. Click **"Create pull request"**
9. **Do NOT click "Merge"** — wait for Omar

Message Omar on WhatsApp: "PR ready for review 🚀"

---

## STEP 5 — Ahmed: Open Pull Request

**Who:** Ahmed

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. Click **"Compare & pull request"** for `feature/finance-sprint2`
3. Set **base: `dev`** ← **compare: `feature/finance-sprint2`**
4. Title: `Sprint 2 (Ahmed): Financial summary and late payment notifications`
5. Description: List what you built
6. Assign **Omar** as reviewer
7. Click **"Create pull request"**
8. **Do NOT click "Merge"**

---

## STEP 6 — Numair: Open Pull Request

**Who:** Numair

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. Click **"Compare & pull request"** for `feature/maintenance-sprint2`
3. Set **base: `dev`** ← **compare: `feature/maintenance-sprint2`**
4. Title: `Sprint 2 (Numair): Maintenance cost reports and date communication`
5. Description: List what you built
6. Assign **Omar** as reviewer
7. Click **"Create pull request"**
8. **Do NOT click "Merge"**

---

## STEP 7 — Omar: Review & Merge All PRs

**Who:** Omar — do each PR one at a time

For each PR on GitHub:
1. Open the PR → click **"Files changed"** tab
2. Check that they only touched their own files
3. Click **"Review changes"** → **"Approve"** → **"Submit review"**
4. Click **"Merge pull request"** → **"Confirm merge"**
5. Wait until merge is confirmed before merging the next one

Then locally:

```bash
git checkout dev
git pull origin dev
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py    # test everything together
```

---

## STEP 8 — Everyone: Pull Updated Dev & Test

**Who:** ALL

```bash
git checkout dev
git pull origin dev
source venv/bin/activate
rm -f pams.db
./venv/bin/python3 seed_db.py
./venv/bin/python3 main.py
```

Test logins:
| Username | Password | Role | What to check |
|----------|----------|------|---------------|
| admin | admin123 | Admin | Sees all tabs including Reports |
| frontdesk1 | pass123 | Front Desk | Sees Tenants with search/filter |
| finance1 | pass123 | Finance Manager | Sees Invoices with overdue badges + Financial Summary |
| maint1 | pass123 | Maintenance | Sees Maintenance with cost report tab |
| manager1 | pass123 | Manager | Sees Reports tab with all 3 report types |

Run the full test suite:
```bash
./venv/bin/python3 -m unittest discover -s tests -v
```

If anything breaks → message Omar. **Do not push a fix to `dev` directly.**

---

## STEP 9 — Sprint Review Meeting

**Who:** ALL — Zoom call

Each member demos their part (2-3 min each):
1. Omar: Reports dashboard (occupancy, financial, maintenance cost), notification system
2. Feras: Tenant search bar, status filter, notification display
3. Ahmed: Financial summary (collected vs pending), overdue badges, late payment alerts
4. Numair: Maintenance cost report by apartment/city, date communication to tenants

Update `BACKLOG.md` together — mark Sprint 2 items `[x]`.

```bash
git checkout dev
git pull origin dev
# Omar updates BACKLOG.md during meeting
git add BACKLOG.md
git commit -m "Sprint 2 complete: all backlog items marked done"
git push origin dev
```

---

## STEP 10 — Omar: Merge `dev` → `main`

**Who:** Omar — only after Sprint Review meeting confirms everything works

```bash
git checkout dev
git pull origin dev

git checkout main
git pull origin main

git merge dev
# Should say "Fast-forward" — no conflicts expected

git push origin main
```

`main` = Sprint 2 complete snapshot. **Nobody pushes directly to main.**

Message team: "`main` updated with Sprint 2. Sprint 3 starts tomorrow!"

---

## 🆘 If Something Goes Wrong

| Problem | Fix |
|:--------|:----|
| `git push` says "rejected, non-fast-forward" | `git pull --rebase origin dev` then push again |
| You edited someone else's file by accident | `git checkout -- path/to/theirfile.py` to undo it, then commit only your files |
| Merge conflict appears | Check `git status`. For files you don't own: `git checkout --theirs <file>` then `git add <file>` |
| You accidentally committed to `dev` directly | `git checkout your-branch`, `git cherry-pick <hash>`, push your branch. Tell Omar. |
| You accidentally committed to `main` | **Stop. Message Omar immediately. Do NOT force-push.** |
| App crashes after pulling | Run `rm -f pams.db && ./venv/bin/python3 seed_db.py` to reset the database |
| "Module not found: customtkinter" | `source venv/bin/activate && pip install -r requirements.txt` |
| Tests fail after pulling | Run `rm -f tests/test_temp.db` then retry. If still failing, message Omar. |
| Totally stuck on anything | **Message Omar on WhatsApp. Do NOT force-push anything.** |
