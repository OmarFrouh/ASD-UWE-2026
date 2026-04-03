# 🚀 Sprint 1 Git Guide — PAMS Group 28
**Last updated:** 30 Mar 2026 | **Branch strategy:** `feature/*` → `dev` → `main` | **Repo:** `OmarFrouh/ASD-UWE-2026`

---

## Progress Tracker

| Step | Date | Task | Owner | Status |
|:-----|:-----|:-----|:------|:-------|
| 0 | 30 Mar | Push foundation + CustomTkinter to `dev` | Omar | ✅ DONE |
| 1 | 30 Mar | Pull `dev`, create `feature/tenant-management`, start coding | Feras | ✅ DONE |
| 2 | 31 Mar | Pull `dev`, create `feature/finance-module`, start coding | Ahmed | ✅ DONE |
| 3 | 31 Mar | Pull `dev`, create `feature/maintenance-module`, start coding | Numair | ✅ DONE |
| 4 | 30 Mar | Push `feature/tenant-management` + PR merged to `dev` (PR #22) | Feras | ✅ DONE |
| 5 | 31 Mar | Push `feature/finance-module` + PR merged to `dev` (PR #23) | Ahmed | ✅ DONE |
| 6 | 31 Mar | Push `feature/maintenance-module` + merged to `dev` | Numair | ✅ DONE |
| 7 | 31 Mar | Review + merge all 3 PRs into `dev` | Omar | ✅ DONE |
| 8 | — | Everyone pulls updated `dev`, confirms app still runs | ALL | ⬜ TODO |
| 9 | 6 Apr | Sprint 1 review meeting | ALL | ⬜ TODO |
| 10 | 6 Apr | Merge `dev` → `main` (Sprint 1 complete snapshot) | Omar | ⬜ TODO |

---

## File Ownership (No one touches a file they don't own)

| File | Owner |
|:-----|:------|
| `main.py` | Omar |
| `database_manager.py` | Omar |
| `auth_manager.py` | Omar |
| `property_manager.py` | Omar |
| `seed_db.py` | Omar |
| `requirements.txt` | Omar |
| `views/login_view.py` | Omar |
| `views/main_view.py` | Omar |
| `views/user_view.py` | Omar |
| `views/apartment_view.py` | Omar |
| `tenant_manager.py` | Feras |
| `views/tenant_view.py` | Feras |
| `invoice_manager.py` | Ahmed |
| `payment_manager.py` | Ahmed |
| `views/invoice_view.py` | Ahmed |
| `views/payment_view.py` | Ahmed |
| `maintenance_manager.py` | Numair |
| `views/maintenance_view.py` | Numair |
| `BACKLOG.md` | Anyone (mark your items done only) |
| `PROJECT_TIMELINE.md` | Omar |
| `TEAM_RESPONSIBILITIES.md` | Omar |

---

## STEP 0 — Omar: Push Foundation to `dev` (30 Mar) ✅ DONE

**Who:** Omar

```bash
cd ~/Desktop/ASD-UWE-2026
source venv/bin/activate
pip install customtkinter
pip freeze > requirements.txt
rm -f pams.db
./venv/bin/python3 seed_db.py

git checkout feature/sprint1-omar
git add -A
git commit -m "Sprint 1 (Omar): CustomTkinter migration, expanded DB schema, role-based sidebar, mock data"
git push origin feature/sprint1-omar

# Merge into dev
git checkout dev
git merge feature/sprint1-omar
git push origin dev

# Message the team: "Sprint 1 foundation pushed. Pull from dev and start your branches!"
```

---

## STEP 1 — Feras: Setup + Tenant Management (31 Mar – 2 Apr) ⬜

**Who:** Feras

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/tenant-management
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads with: admin / admin123
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/tenant-management && git merge dev`

**Your files to create** (from `guides/SPRINT1_FERAS.md`):
- `tenant_manager.py`
- `views/tenant_view.py`

```bash
# After coding:
git add tenant_manager.py views/tenant_view.py
git commit -m "Sprint 1 (Feras): tenant registration, list, early termination, archive"
git push origin feature/tenant-management
```

**Also do:** Draw Use Case Diagram in Astah (steps in `guides/SPRINT1_FERAS.md` → Step 4)

---

## STEP 2 — Ahmed: Setup + Finance Module (31 Mar – 2 Apr) ⬜

**Who:** Ahmed

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/finance-module
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/finance-module && git merge dev`

**Your files to create** (from `guides/SPRINT1_AHMED.md`):
- `invoice_manager.py`
- `payment_manager.py`
- `views/invoice_view.py`
- `views/payment_view.py`

```bash
# After coding:
git add invoice_manager.py payment_manager.py views/invoice_view.py views/payment_view.py
git commit -m "Sprint 1 (Ahmed): invoice generation, payment recording, overdue tracking"
git push origin feature/finance-module
```

---

## STEP 3 — Numair: Setup + Maintenance Module (31 Mar – 2 Apr) ⬜

**Who:** Numair

```bash
cd ~/Desktop/ASD-UWE-2026
git checkout dev
git pull origin dev
git checkout -b feature/maintenance-module
source venv/bin/activate
pip install -r requirements.txt
./venv/bin/python3 main.py    # confirm the app loads
```

> ⚠️ **Every time you sit down to code:** `git checkout dev && git pull origin dev && git checkout feature/maintenance-module && git merge dev`

**Your files to create** (from `guides/SPRINT1_NUMAIR.md`):
- `maintenance_manager.py`
- `views/maintenance_view.py`

```bash
# After coding:
git add maintenance_manager.py views/maintenance_view.py
git commit -m "Sprint 1 (Numair): maintenance tickets, staff assignment, cost logging"
git push origin feature/maintenance-module
```

---

## STEP 4 — Feras: Open Pull Request (2 Apr) ⬜

**Who:** Feras

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. You'll see a yellow banner: **"Compare & pull request"** for `feature/tenant-management`
3. Click it
4. Set **base: `dev`** ← **compare: `feature/tenant-management`**
5. Title: `Sprint 1 (Feras): Tenant registration and management`
6. Description: List what you built (registration form, tenant list, early termination, archive)
7. Assign **Omar** as reviewer (right sidebar → "Reviewers")
8. Click **"Create pull request"**
9. **Do NOT click "Merge"** — wait for Omar

Message Omar on WhatsApp: "PR ready for review 🚀"

---

## STEP 5 — Ahmed: Open Pull Request (2 Apr) ⬜

**Who:** Ahmed

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. Click **"Compare & pull request"** for `feature/finance-module`
3. Set **base: `dev`** ← **compare: `feature/finance-module`**
4. Title: `Sprint 1 (Ahmed): Invoice and payment module`
5. Description: List what you built
6. Assign **Omar** as reviewer
7. Click **"Create pull request"**
8. **Do NOT click "Merge"**

---

## STEP 6 — Numair: Open Pull Request (2 Apr) ⬜

**Who:** Numair

1. Go to **https://github.com/OmarFrouh/ASD-UWE-2026**
2. Click **"Compare & pull request"** for `feature/maintenance-module`
3. Set **base: `dev`** ← **compare: `feature/maintenance-module`**
4. Title: `Sprint 1 (Numair): Maintenance module`
5. Description: List what you built
6. Assign **Omar** as reviewer
7. Click **"Create pull request"**
8. **Do NOT click "Merge"**

---

## STEP 7 — Omar: Review & Merge All PRs (3 Apr) ⬜

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

## STEP 8 — Everyone: Pull Updated Dev & Test (3 Apr) ⬜

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
|----------|----------|------|--------------|
| admin | admin123 | Admin | Sees all tabs |
| frontdesk1 | pass123 | Front Desk | Sees Tenants tab |
| finance1 | pass123 | Finance Manager | Sees Invoices + Payments |
| maint1 | pass123 | Maintenance | Sees Maintenance |
| manager1 | pass123 | Manager | Sees Reports |

If anything breaks → message Omar. **Do not push a fix to `dev` directly.**

---

## STEP 9 — Sprint Review Meeting (6 Apr) ⬜

**Who:** ALL — Zoom call

Each member demos their part (2-3 min each):
1. Omar: Login, roles, dashboard stats, add apartment
2. Feras: Register tenant, view tenants, early termination
3. Ahmed: Generate invoice, record payment, overdue list
4. Numair: Create ticket, assign staff, log costs

Update `BACKLOG.md` together — mark Sprint 1 items `[x]`.

```bash
git checkout dev
git pull origin dev
# Omar updates BACKLOG.md during meeting
git add BACKLOG.md
git commit -m "Sprint 1 complete: all backlog items marked done"
git push origin dev
```

---

## STEP 10 — Omar: Merge `dev` → `main` (6 Apr) ⬜

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

`main` = Sprint 1 complete snapshot. **Nobody pushes directly to main.**

Message team: "`main` updated with Sprint 1. Sprint 2 starts tomorrow!"

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
| Totally stuck on anything | **Message Omar on WhatsApp. Do NOT force-push anything.** |
