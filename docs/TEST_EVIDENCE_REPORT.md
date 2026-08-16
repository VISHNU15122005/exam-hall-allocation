# Tactive Assessment — Test Evidence Report

## Exam Hall Allocation System

**Deliverable:** Test suite + captured execution evidence + deliberate RED run  
**Evidence basis:** Recorded Claude development/testing session

> This document is intentionally evidence-first. Where the source session did not verify a detail, it is explicitly marked as not verified rather than inferred.

---

## 1. Executive Summary

The Exam Hall Allocation System assigns students to examination seats across one or more halls while enforcing capacity limits, preventing duplicate seat assignments, validating imported student data, and rendering the seating plan. The latest feature adds a preference to avoid seating students from the same Class/Section next to one another whenever possible.

The verified unit-level result is **67 passed, 0 failed** in a fresh virtual environment. A broader `tests/` run produced **1 failed, 67 passed, 229 warnings in 10.99s**; the recorded session attributes the single failure to the Playwright integration/E2E environment limitation, but the exact failing traceback was not captured in the audit excerpt.

---

## 2. Evidence Result Status

| Evidence Stage | Result | Status |
|---|---:|---|
| Baseline before adjacency feature | 60 passed, 0 failed | GREEN |
| Deliberate capacity defect | 1 failed, 12 warnings | EXPECTED RED |
| Restoration | Suite returned to green | RECOVERED |
| Targeted AI change-loop slice | 21/21 reported passing | GREEN |
| Final unit suite | 67 passed, 0 failed | VERIFIED GREEN |
| Broader suite | 1 failed, 67 passed, 229 warnings | PARTIAL / E2E LIMITATION |

The source report explicitly preserves the discrepancy between the 60-test baseline, 8 new adjacency tests, 21/21 targeted result, and final 67-test unit suite rather than silently reconciling those figures.

---

## 3. Application Scope

### Main evidenced workflow

```text
Login
  ↓
Upload student data
  ↓
Preview
  ↓
Confirm import
  ↓
Manage halls
  ↓
Generate allocation
  ↓
View seating
  ↓
Search / Export
  ↓
Run tests + RED/AI change-loop evidence
```

### Core functionality

- Hall creation and management
- Student import and validation
- Exam-session creation/persistence
- Seat allocation
- Multi-hall allocation
- Capacity-boundary handling
- Idempotent allocation re-run
- Seating-plan rendering
- Admin authentication
- Class/Section adjacency avoidance

---

## 4. Test Strategy

### 4.1 Unit testing

Seven files under `tests/unit/` cover validators, import service, allocation service, authentication routes, halls routes, imports routes, and seating routes. The clean unit run was independently re-verified in a fresh virtual environment.

**Result:** `67 passed, 0 failed`

### 4.2 Negative testing

The suite checks:

- Missing register number
- Missing student name
- Missing subject
- Missing exam date
- Missing exam time
- Invalid exam date
- Invalid exam time
- Duplicate register number within a session
- Invalid register-number characters
- Empty rows
- Empty batches
- Invalid file format
- Missing required columns
- Missing required columns in XLSX

### 4.3 Edge-case testing

The suite also covers:

- Exact hall capacity
- Single-seat/single-student boundary
- One-student-over-capacity boundary
- Inactive halls
- Multiple halls
- Re-running allocation
- Multiple independent exam sessions
- Adjacency fallback when no non-adjacent seat exists
- Independent adjacency behavior within each hall

### 4.4 Manual verification

The application was exercised once through the login/dashboard flow:

```text
Fresh venv
  → install dependencies
  → start server
  → GET /login → 200
  → POST /login with admin/admin123
  → GET / → 200
  → "Dashboard" present
```

This was recorded as a successful manual verification.

### 4.5 Integration / E2E

`tests/integration/test_e2e_workflow.py` exists, but Playwright could not be executed successfully in the recorded sandbox because a working Chromium environment was unavailable and the environment had restricted network access.

**Status: NOT VERIFIED**

---

## 5. Test Environment

| Item | Evidence |
|---|---|
| Runtime | Python virtual environment |
| Framework | Flask |
| Test framework | pytest |
| Browser test | Playwright |
| Data/model layer | SQLAlchemy implied by project/test evidence |
| OS | Not stated in session |
| Python version | Not stated |
| pytest version | Not stated |
| Exact database engine | Not stated |
| Execution setup | Fresh venv + `pip install -r requirements.txt` |

The source report intentionally does not guess missing environment information.

---

## 6. Test Coverage Matrix

### Allocation

| Scenario | Expected | Test | Status |
|---|---|---|---|
| Every student receives one seat | 1 seat per valid student | `test_each_student_receives_exactly_one_seat` | PASS |
| Allocation route | Redirect to seating | `test_generate_allocation_route_allocates_and_redirects_to_seating` | PASS |
| Multiple halls | Overflow uses additional halls | `test_allocation_spans_multiple_halls_when_needed` | PASS |
| Re-run allocation | No duplicate seats | `test_re_running_allocation_does_not_duplicate_seats` | PASS |
| Independent sessions | No cross-session conflict | `test_multiple_independent_exam_sessions_reuse_same_halls_without_conflict` | PASS |
| Exact capacity | All seats filled | `test_hall_capacity_exactly_equals_student_count` | PASS |
| Single-seat boundary | Student seated | `test_boundary_single_seat_hall_with_single_student` | PASS |
| Over-capacity boundary | Extra student unallocated | `test_boundary_one_student_more_than_capacity_is_unallocated` | PASS |
| Inactive halls | Excluded | `test_inactive_halls_are_not_used` | PASS |

### Adjacency

| Scenario | Expected | Test | Status |
|---|---|---|---|
| No suitable non-adjacent seat | Seat everyone anyway | `test_adjacency_rule_yields_to_seating_everyone_when_no_choice_exists` | PASS |
| Per-hall behavior | No cross-hall adjacency effect | `test_adjacency_avoidance_works_independently_within_each_hall` | PASS |

### Import and validation

The named test set validates successful persistence and a broad negative-path matrix for required fields, date/time formats, duplicate register numbers, invalid characters, empty data, file format and required-column failures.

### Hall, seating and authentication

Hall persistence, independent hall creation, seating-plan rendering, and admin login are explicitly covered and reported as passing.

---

## 7. Baseline GREEN Run

Before the adjacency feature was introduced, the source session established:

**60 tests collected → 60 passed → 0 failed**

The exact command, warning count, skipped count and execution duration were not shown in the session excerpt.

This baseline is important because it establishes that the pre-existing suite was green before the change.

---

## 8. Deliberate RED Run

### Business rule under protection

> Hall capacity must never be exceeded.

### Intentional defect

The capacity comparison in `allocation_service.py` was changed by one character:

```python
# Correct
>=

# Deliberately incorrect
>
```

### Observed failure

```text
IndexError: list index out of range
allocation_service.py:115

1 failed, 12 warnings in 0.78s
```

### Root cause

Changing `>=` to `>` weakened the capacity guard. The allocator was then allowed to attempt seating one more student than the available hall capacity, producing an out-of-range seat access.

### Restoration

The defect was reverted and the source session reports that the restored file was verified **byte-for-byte identical** to the original implementation using `diff`.

The original raw RED output is referenced by the source report as:

`docs/evidence/deliberate-red-output.txt` — 114 lines.

---

## 9. AI Change Loop

### Feature request

> Modify the Exam Hall Allocation System so that students from the same class/section should not be seated next to each other whenever possible. Requirements: every valid student gets exactly one seat; no seat assigned twice; hall capacity never exceeded; multiple halls continue working; existing validation continues working; no regression.

### Adjacency definition

Two seats are considered adjacent only when:

- They are in the same hall
- They are in the same row
- Their column numbers differ by exactly 1

Different rows and different halls are not considered adjacent.

### Allocation strategy

1. Preserve existing register-number processing order.
2. Inspect remaining free seats.
3. Prefer the first free seat with no same-Class/Section neighbor.
4. If no such seat exists, fall back to the first remaining free seat.
5. Preserve the higher-priority rule that students should still be seated.

---

## 10. AI Attempts

### Attempt 1

- Implemented adjacency avoidance.
- Added 8 adjacency-specific tests.
- Existing 60 tests remained green.
- 2 of the 8 new tests failed.
- Investigation found a combinatorial mathematics error in the AI-generated test assertions, not in the application implementation.
- The correction was independently checked using `math.ceil(3/2)`.

### Attempt 2

- Corrected the two faulty assertions.
- Targeted slice reported **21/21 passing**.
- No further failure was reported for that targeted loop.

### Important evidence note

The source report preserves the numbers **60**, **8**, **21/21**, and **67** because their relationship was not fully explained during the session. This document does not invent a reconciliation.

---

## 11. Security Review

### Verified protections

- Password hashing through Werkzeug
- `@login_required` on admin routes
- Secure filename handling for uploads
- File-extension allow-list
- File-size limit
- Immediate deletion after upload processing
- No raw `text()` / `execute()` SQL usage found during the recorded grep review
- No `|safe` filter or `Markup()` usage found
- `.env` excluded through `.gitignore`
- `.env.example` contains placeholders

### Open findings

1. No CSRF protection on POST forms.
2. `debug=True` remains in the production entry point.
3. `SECRET_KEY` has an insecure fallback value.
4. No login rate limiting.

These are documented findings, not claims that the application is production-secure.

---

## 12. Warnings and Limitations

The broad run reported **229 warnings**, but the session did not preserve enough detail to identify every warning type/source.

The most important limitations are:

- Playwright E2E was not shown passing.
- Git history was unavailable because no `.git` directory existed in the working copy.
- The AI test-count figures remain unreconciled.
- No presentation file existed in the original repository.
- No 5-minute demo recording existed.
- The original pre-defect code snippet and individually named RED test were not preserved in the session excerpt.

---

## 13. Final Evidence Summary

| Stage | Evidence |
|---|---|
| Baseline | 60 passed, 0 failed |
| RED run | 1 failed, 12 warnings |
| RED defect | `>=` changed to `>` |
| RED error | `IndexError` at `allocation_service.py:115` |
| Restoration | Byte-for-byte verified |
| AI Attempt 1 | 60/60 existing; 2/8 new failed |
| AI Attempt 2 | 21/21 targeted slice |
| Final unit | 67 passed, 0 failed |
| Broader suite | 1 failed, 67 passed, 229 warnings |
| E2E | Not verified |

---

## 14. Submission Readiness Actions

Before final submission:

1. Reconcile the 60 / 8 / 21 / 67 test-count figures.
2. Run `tests/integration/test_e2e_workflow.py` with working Chromium.
3. Confirm OS, Python, pytest and database versions from the actual project.
4. Fix or explicitly accept the CSRF, debug-mode and SECRET_KEY issues.
5. Inspect real Git history for `.env` and database files.
6. Resolve the `AI_CHANGE_LOOP.md` / `ai-change-loop.md` case collision.
7. Remove or update stale `docs/test-strategy.md`.
8. Create the presentation.
9. Record and time the 5-minute demo video.

---

## 15. Evidence Integrity Statement

This report intentionally separates:

- **Verified evidence**
- **Reported aggregate results**
- **Environment limitations**
- **Unresolved discrepancies**

No screenshot, raw terminal line, test count, environment detail, or security result is invented where the source session did not provide it.
