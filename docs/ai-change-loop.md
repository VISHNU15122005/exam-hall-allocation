# AI Change Loop

## Status

**Not yet performed.** Per the assessment brief, the adjacency/class-section
seating rule is deliberately left out of the initial implementation so that
*you* can run the full change loop yourself (implement → test → fail →
diagnose → fix → pass) with an AI coding assistant and capture genuine
evidence, rather than have it pre-baked and faked here. This document gives
you everything needed to run it in one sitting.

## Feature Request (use this exact prompt)

> Modify the seating allocation algorithm so that, whenever possible,
> students from the same class or section are not assigned to adjacent
> seats, while preserving all existing capacity, uniqueness, and allocation
> rules.

## What Exists Already (relevant to this change)

- `Student.class_section` — already a column, already populated from the
  optional "Class/Section" column during import (see
  `app/services/import_service.py` `COLUMN_ALIASES["class_section"]`), so
  no schema or import change is needed — the sample data in
  `sample_data/students.xlsx` already includes a Class/Section column
  (`CSE-A` / `CSE-B`).
- `Seat.row_label` / `Seat.col_number` give you adjacency: two seats are
  "adjacent" if they're in the same row with `col_number` differing by 1
  (extend to include diagonal/row-below neighbors if you want a stricter
  definition — state whichever definition you pick in your submission).
- The allocation loop in `generate_allocation()` currently assigns seats in
  strict `free_slots` order with no look-ahead — that's the function you'll
  change.

## Suggested Loop (run this with Claude Code, Cursor, etc.)

1. **Baseline:** run `pytest tests/unit/test_allocation_service.py -v` and
   confirm all 9 tests pass before changing anything. Save this output.
2. **Prompt the AI** with the feature request above, pointing it at
   `app/services/allocation_service.py`.
3. **Implement:** a reasonable approach is to sort students by
   `class_section` into separate queues and interleave the queues when
   pulling from `free_slots` (round-robin across sections) instead of
   pulling students in strict register-number order — so consecutive seats
   rarely come from the same section. This must not change the existing
   rule enforcement (capacity, uniqueness, no double-booking).
4. **Re-run the existing suite.** A likely first failure: if the
   AI changes the order students are processed in, tests that assert
   *which* register number ends up unallocated when capacity is short
   (e.g. `test_insufficient_capacity_reports_unallocated_students` only
   checks *counts*, so it should be safe — but double-check any test you
   add that asserts a specific student-to-seat mapping).
5. **Add new tests** for the adjacency rule itself, e.g.
   `test_same_section_students_are_not_seated_adjacently_when_avoidable`
   and `test_adjacency_rule_yields_to_capacity_when_no_choice_exists`
   (i.e. when every remaining seat is adjacent to same-section students,
   the engine must still seat everyone rather than leave students
   unallocated).
6. **Iterate** until the full suite (old + new tests) passes. Record every
   attempt.

## Evidence to Capture for Submission

```
Prompt used            → (paste exact text)
Files changed           → app/services/allocation_service.py, +tests
AI's first implementation → (diff or summary)
Test run #1             → PASS/FAIL list, exact pytest output
Failure analysis         → what broke and why
Fix applied              → (diff or summary)
Test run #2 (repeat as needed)
Final result             → full green run, pytest output
Number of attempts       → N
Manual intervention      → state honestly if you had to correct the AI's fix
```

Do not summarize this as "worked first try" unless it genuinely did —
the assessment specifically checks for real failure-and-correction
evidence, not a clean narrative.
