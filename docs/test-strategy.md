# Test Strategy

## Objectives

Prove the allocation engine and import pipeline behave correctly under
normal, edge, and invalid conditions, and provide a genuine
red-run → fix → green-run cycle plus an AI change-loop demonstration, per
the assessment requirements.

## Test Categories & Location

| Category | Location | Tooling |
|---|---|---|
| Row/batch validation (pure logic) | `tests/unit/test_validators.py` | pytest |
| File parsing / column normalization | `tests/unit/test_import_service.py` | pytest |
| Allocation engine business rules | `tests/unit/test_allocation_service.py` | pytest (needs Flask-SQLAlchemy) |
| Full browser workflow | `tests/integration/test_e2e_workflow.py` | Playwright |

## Coverage Summary

**Normal:** valid CSV/XLSX import, successful single-hall allocation,
allocation spanning multiple halls, seating plan renders, student search
returns a match.

**Edge:** exactly-enough seats, one-seat-short, re-running allocation is
idempotent (no duplicate seats), inactive halls excluded, empty exam
session, alternate date/time formats.

**Invalid:** missing register number/name/subject/date/time, invalid date,
invalid time, duplicate register number within a session, empty file,
missing required column, unrelated columns silently dropped (not
accepted), same student double-booked at identical date/time, allocation
attempted with no active halls.

## What Was Actually Executed in This Environment

This build environment has **no network access**, so `pip install` could
not run and packages not already preinstalled (`flask_sqlalchemy`,
`flask_login`, `pytest`, `playwright`) are unavailable here. Rather than
claim a pytest run that didn't happen, here is exactly what was and wasn't
verified in this sandbox:

- **Verified, for real, in this sandbox:** `tests/unit/test_validators.py`
  (13 tests) and `tests/unit/test_import_service.py` (6 tests) were executed
  directly (bypassing the Flask package import, via
  `tests/unit/_run_standalone.py`, a dev-only helper — not part of the
  delivered suite) because they have no Flask/DB dependency. Result:
  **19/19 passed**, actual output, not fabricated.
- **Written but not executed here:** `test_allocation_service.py` and the
  Playwright e2e test require Flask-SQLAlchemy / Flask-Login / a running
  server, none of which could be installed without network access. All
  files were syntax-checked (`python -m py_compile`, all pass) and reviewed
  line-by-line against the business rules in `docs/design.md`, but you
  should run them yourself after `pip install -r requirements.txt` to get a
  real pass/fail result — see "Running Tests" in the README.

## Deliberate Red Run (for you to perform and capture)

This step needs a real local environment (network access to `pip install`),
so it's documented here as a precise, reproducible procedure rather than a
result claimed by this sandbox.

1. Open `app/services/allocation_service.py`.
2. In the slot-assignment loop, change:
   ```python
   if slot_index >= len(free_slots):
   ```
   to:
   ```python
   if slot_index > len(free_slots):   # BUG: off-by-one, allows one extra student
   ```
3. Run:
   ```bash
   pytest tests/unit/test_allocation_service.py -v
   ```
4. Expected real output: `test_allocation_never_exceeds_hall_capacity` fails,
   because `IndexError` is raised (or, depending on Python's list
   indexing, an out-of-range access) when `slot_index == len(free_slots)`
   — one student is pulled past the end of the `free_slots` list. Capture
   the actual pytest failure output for your submission.
5. Revert the change (back to `>=`) and re-run to confirm a clean pass.
   Record before/after output side by side in your submission per the
   assessment's red-run requirement.

## AI Change Loop

See `docs/ai-change-loop.md`.
