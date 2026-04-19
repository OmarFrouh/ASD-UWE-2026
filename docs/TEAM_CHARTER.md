# Team Charter / Working Agreement

**Date**: 02/03/2026
**Group Number**: 28
**Module**: UFCF8S-30-2 Advanced Software Development

## 1. Communication
*   **Primary Channel**: WhatsApp Group
*   **Response Time**: We agree to respond to messages within **24 hours** on weekdays.
*   **Availability**: We are available Monday to Friday mornings, excluding Wednesdays.

## 2. Meetings
*   **Weekly Stand-up**: Every Monday on a Zoom call.
*   **Attendance**: Mandatory. If you cannot make it, you must notify the Scrum Master 2 hours in advance.
*   **Consequences**: Missing 2 meetings without notice will be raised with the module tutor.

## 3. Work Process (Git & Development)
*   **Branching**: We will use the "Feature Branch" workflow. No one commits directly to `main`.
*   **Commit Messages**: Must be descriptive (e.g., "Added login button logic" not "update").
*   **Code Review**: All Pull Requests must be approved by at least 1 other member before merging.
*   **Definition of Done**: A feature is "Done" when:
    *   It runs without errors.
    *   The code is commented with the author's name and student ID.
    *   It has been pushed to the repo and merged into `dev`.
    *   Automated tests cover the new behaviour.

## 4. Conflict Resolution
*   If we disagree on a technical decision, we will vote. In a tie, the Group Leader makes the final call.
*   If a member is not contributing, we will:
    1.  Talk to them privately (Leader).
    2.  Discuss it as a group.
    3.  Escalate to Module Tutor with evidence (Git logs).

## 5. Signatures
(By adding your name here, you agree to these rules)
*   Omar Alfrouh
*   Feras Bader
*   Ahmed Deraz
*   Numair

---

## How We Stuck to the Charter (retrospective, Apr 2026)

Recorded at the end of Sprint 4 so the charter is not just a signed page — it is a record of what we actually did.

*   **Communication**: WhatsApp remained our main channel across all 4 sprints. Response time held to within a day on weekdays.
*   **Meetings**: Weekly Monday stand-ups were held each sprint (4 total). Sprint planning was done in the same meeting that closed the previous sprint.
*   **Branching**: We stayed on the feature-branch workflow end-to-end. All Sprint 2, 3 and 4 merges went through PRs (#22, #24, #26, #27, #28, #29). No direct pushes to `main`. The `main` branch only moved when `dev` was merged at the end of a sprint.
*   **Code Review**: Omar reviewed every PR before merging. PR descriptions referenced the brief requirement they delivered.
*   **Commit Messages**: We kept commit messages short and descriptive. `git log --oneline main` reads as a plain change log.
*   **Definition of Done**: Held consistently — every merged feature had author + student ID in the file header and unit-test coverage. The test suite grew from 93 tests (Sprint 1) to 330 tests (Sprint 4).
*   **Conflict Resolution**: No formal votes were needed. Scope disagreements (e.g., should the 1-month notice change the method signature from tuple to dict) were discussed in the stand-up and resolved the same day.
