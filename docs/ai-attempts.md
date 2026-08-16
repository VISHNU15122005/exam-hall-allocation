# AI Attempts

## Attempt 0 — Baseline

**Purpose:** establish regression safety.

Result:
`60 passed, 0 failed`

---

## Attempt 1 — Feature Implementation

### Action
Implemented Class/Section adjacency avoidance and added 8 new adjacency tests.

### Result
Existing tests:
`60/60 passed`

New tests:
`2/8 failed`

### Diagnosis
The source report states that the failures were caused by a combinatorial mathematics error in two AI-generated assertions.

### Correction
The two test assertions were corrected. The source report states that the arithmetic was independently checked using `math.ceil(3/2)`.

---

## Attempt 2 — Corrected Tests

### Action
Reran the corrected targeted tests.

### Result
`21/21 passing`

### Status
Targeted feature slice considered complete.

---

## Deliberate RED Evidence

### Action
Changed allocation capacity guard from `>=` to `>`.

### Result
`1 failed, 12 warnings in 0.78s`

### Failure
`IndexError: list index out of range at allocation_service.py:115`

### Correction
Restored `>=` and verified byte-for-byte restoration.

---

## Final Verification

Unit-only:
`67 passed, 0 failed`

Broader suite:
`1 failed, 67 passed, 229 warnings in 10.99s`

The broader-suite failure remains associated with the unverified Playwright environment limitation in the source report.
