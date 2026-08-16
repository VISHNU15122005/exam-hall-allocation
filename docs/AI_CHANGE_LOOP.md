# Tactive Assessment — AI Change-Loop Evidence Log

## Exam Hall Allocation System

**Deliverable:** AI prompts, implementation attempts, failures, diagnosis, corrections and verification

---

## 1. Change-Loop Objective

The goal of the change loop was to add a new allocation preference:

> Students from the same Class/Section should not be seated next to each other whenever possible.

The feature had to preserve the existing higher-priority requirements:

- Every valid student receives a seat.
- No seat is assigned twice.
- Hall capacity is never exceeded.
- Multiple halls continue to work.
- Existing validation continues to work.
- No regression in the existing suite.

---

## 2. AI Tool

**Claude** was used as the coding/testing agent.

The recorded session shows Claude performing implementation, test execution, interpretation of failures, correction of generated tests, security review, documentation updates and evidence reporting.

---

## 3. Initial Project State

The existing unit suite was first established as a GREEN baseline:

**60 passed, 0 failed**

This baseline was used to detect regressions introduced by the new adjacency feature.

---

## 4. Feature Design

### 4.1 Adjacency definition

Two seats are adjacent only when they are:

```text
Same Hall
   +
Same Row
   +
Column difference = 1
```

Therefore:

```text
[Seat 1] [Seat 2]  ← adjacent
[Seat 3] [Seat 4]  ← different row, not adjacent
```

Seats in different halls are never adjacent.

### 4.2 Student ordering

Students continue to be processed in their existing register-number order. The source report explicitly states that students were not reordered because existing tests may depend on processing order.

### 4.3 Seat-selection logic

```text
For each student
      ↓
Find remaining free seats
      ↓
Is there a free seat with
no same-Class/Section neighbor?
      ↓
   YES ─────────────→ Assign preferred seat
      │
      NO
      ↓
Assign first remaining free seat
      ↓
Continue until students are processed
```

The fallback preserves the higher-priority requirement that seating everyone takes precedence over the adjacency preference.

---

## 5. Files Changed

The recorded session identifies the following change areas:

- Allocation service / allocation engine
- Adjacency-specific tests
- `README.md`
- `docs/AI_CHANGE_LOOP.md`
- `docs/architecture.md`
- `docs/design.md`
- `docs/user-guide.md`

The allocation engine received the feature logic, while tests were expanded to cover adjacency behavior.

---

## 6. Attempt 1

### AI action

Claude implemented the Class/Section adjacency rule and added **8 new adjacency-specific tests**.

### Regression result

The existing baseline suite remained green:

**60/60 existing tests passed**

This is important because the feature implementation did not immediately break the established regression suite.

### New-test result

**2 of 8 new adjacency tests failed.**

### Investigation

The failure was traced to the test assertions themselves.

The source report states that the problem was a **combinatorial mathematics error in two AI-generated tests**, not an error in the allocation implementation.

The reasoning was independently checked using:

```python
math.ceil(3/2)
```

### Correction

The two faulty test assertions were corrected to reflect the correct combinatorics.

---

## 7. Attempt 2

### AI action

Claude reran the corrected targeted tests.

### Result

The source report records:

**21/21 passing**

No further failure was reported for that targeted slice.

The feature was therefore considered complete for the change-loop attempt.

---

## 8. Deliberate RED Run

The Tactive evidence requirement also required a controlled failure.

A separate deliberate defect was introduced into the capacity guard:

```python
# Correct
>=

# Deliberately broken
>
```

### Protected business rule

A hall must never be allowed to exceed its capacity.

### Result

```text
IndexError: list index out of range
allocation_service.py:115

1 failed, 12 warnings in 0.78s
```

### Diagnosis

The `>` condition allowed an additional allocation attempt at the exact capacity boundary.

### Restoration

The original `>=` condition was restored and byte-for-byte equality with the original source was verified through a diff.

---

## 9. AI-Assisted Debugging Beyond the Feature

The session also recorded other engineering failures and corrections:

### Environment issue

`seed.py` was initially executed from the wrong directory. After moving into the project directory, Flask was initially unavailable in the active environment.

The environment was corrected by using the project virtual environment and required dependencies.

### Admin JavaScript issue

The Admin dashboard initially displayed machines but Add/Edit functionality failed.

The investigation identified:

- `loadAdminMachines` undefined
- JavaScript loading/function-scope problems
- Modal accessibility issues
- `Illegal return statement`

The Admin modal/JavaScript structure was corrected and the machine-management UI became functional.

### Static-file/server issue

A temporary browser check produced:

```text
ERR_CONNECTION_REFUSED
```

The Flask server was restarted, `admin.js` was checked, and the static file returned HTTP 200.

### Admin date-filter issue

The first date-filter implementation produced:

```text
assert 403 == 200
```

for two Admin tests.

The Admin authentication/test fixture was reviewed and corrected. The complete suite subsequently reached the reported final passing state.

---

## 10. Final Verification

The source report records the final unit command:

```text
pytest tests/unit -v
```

Result:

```text
67 passed, 0 failed
```

The broader command:

```text
python -m pytest tests/ -v
```

produced:

```text
1 failed, 67 passed, 229 warnings in 10.99s
```

The session attributes the broader-suite failure to the Playwright E2E environment limitation, while explicitly noting that the exact traceback was not shown.

---

## 11. Attempt Summary

| Attempt | Change | Result | Diagnosis | Correction |
|---|---|---|---|---|
| Baseline | Existing suite | 60/60 pass | No issue | Establish baseline |
| Attempt 1 | Adjacency + 8 tests | 2/8 new tests failed | AI test math error | Corrected assertions |
| Attempt 2 | Corrected tests | 21/21 targeted pass | No application defect found | Complete |
| RED evidence | Capacity guard deliberately broken | 1 failed, 12 warnings | `>=` → `>` | Reverted |
| Final unit | Full unit suite | 67 pass | Green | Verified |

---

## 12. AI Change Loop Model

```text
Requirement
     ↓
AI Implementation
     ↓
Automated Test
     ↓
Failure / Evidence
     ↓
Root-Cause Analysis
     ↓
Correction
     ↓
Retest
     ↓
Verified Result
```

This was not a single-shot AI generation. The recorded evidence contains real failures, debugging and corrections.

---

## 13. Test-Count Reconciliation Warning

The source session deliberately preserves an unresolved discrepancy:

- 60 baseline tests
- 8 new adjacency tests
- 2 of those 8 initially failed
- 21/21 targeted tests later passed
- 67 final unit tests passed

Mathematically, 60 + 8 would suggest 68, not 67. The report therefore does not claim a definitive reconciliation.

This should be clarified before final submission.

---

## 14. Human / AI Responsibility

The recorded session states that Claude acted as the coding/testing agent.

Human involvement evidenced in the session included:

- Providing the feature requirement
- Requesting the audit/evidence report
- Requesting deliverable verification

The transcript does not provide enough detail to quantify which individual code changes were manually edited after Claude generated them.

---

## 15. Evidence Integrity

The change-loop record distinguishes application failures from test-authoring failures.

The two initial adjacency failures were not silently labelled as application bugs. Instead, the source report identifies them as test assertion errors and records their correction.

Likewise, the Playwright limitation is recorded as **not verified**, rather than being presented as a passing E2E result.
