# Design

## Database Schema

```
Admin
  id, username, password_hash, created_at

ExamSession        (unique: subject + exam_date + exam_time)
  id, subject, exam_date, exam_time

Student            (unique: register_number + exam_session_id)
  id, register_number, student_name, class_section,
  exam_session_id -> ExamSession, import_batch_id -> ImportBatch

Hall
  id, name, code (unique), rows, cols, is_active
  capacity = rows * cols  (derived property, not stored, so it can never drift)

Seat               (unique: hall_id + label)
  id, hall_id -> Hall, row_label, col_number, label   e.g. "A12"

Allocation         (unique: student_id + exam_session_id)
                   (unique: exam_session_id + hall_id + seat_id)
  id, student_id -> Student, exam_session_id -> ExamSession,
  hall_id -> Hall, seat_id -> Seat, seat_label, created_at

ImportBatch
  id, filename, uploaded_at, total_rows, valid_rows, invalid_rows, admin_id
```

The two `Allocation` unique constraints are the database-level enforcement of
Rules 1/2/4 below — even a bug in the allocation loop cannot produce a
duplicate seat or double-booked student, because the insert itself would fail.

## Allocation Algorithm

1. Load the `ExamSession` and all its `Student` rows, ordered by register
   number (deterministic output).
2. Load all **active** halls; build the list of free `(Hall, Seat)` slots not
   already used in this session (`ensure_seats()` lazily creates `Seat` rows
   the first time a hall is used).
3. Walk students in order. For each:
   - Skip if already allocated for this session (idempotent re-run).
   - Reject (unallocated, reason "scheduling conflict") if the same
     register number is already seated in a different session at the exact
     same date/time (Rule 8).
   - Reject (unallocated, reason "insufficient hall capacity") if no free
     slot remains.
   - Otherwise take the next free `(Hall, Seat)` slot.
4. Commit all allocations in one transaction; return allocated + unallocated
   lists so the UI can show both a success count and a shortfall warning.

## Business Rules → Where Enforced

| Rule | Enforcement |
|---|---|
| 1. Every student gets exactly one seat | Allocation loop assigns one slot per student; DB unique constraint backs it up |
| 2. One seat → one student | `free_slots` pool is consumed, never reused within a run; DB unique constraint on (session, hall, seat) |
| 3. Hall capacity never exceeded | `free_slots` is built strictly from real `Seat` rows (rows × cols); nothing beyond that pool can be assigned |
| 4. No student allocated twice | `already_allocated_ids` check before assigning |
| 5. Duplicate register numbers rejected | `student_validator.validate_batch()` at import time |
| 6. Only session's own students allocated | `session.students` query is scoped to the session |
| 7. Insufficient capacity reported | `unallocated` list returned with a reason per student |
| 8. No double-booking at same date/time | `_student_has_conflicting_allocation()` cross-session check |

## Validation Rules

Implemented in `validators/student_validator.py`, applied per-row then
per-batch:

- Required: register number, student name, subject, exam date, exam time
- Register number: alphanumeric + `- _ /`, 2–30 chars
- Date: accepts `YYYY-MM-DD`, `DD-MM-YYYY`, `DD/MM/YYYY`, `DD-Mon-YYYY`,
  `DD Mon YYYY`, `MM/DD/YYYY`
- Time: accepts `HH:MM AM/PM`, `24-hour HH:MM`, `HH AM/PM`, `HH:MM:SS`
- Duplicate detection: same register number + subject + date + time within
  one uploaded batch (a student *can* legitimately appear once per distinct
  exam)

## Error Handling

- File-level errors (empty/corrupt/unsupported/missing columns) raise
  `ImportParseError` with a specific, user-safe message — never a raw
  traceback — and are shown via a flash message.
- Row-level errors are collected per row and shown in the import preview
  table; nothing is saved to the database until the admin explicitly
  confirms.
- Allocation-level errors (`AllocationError`: no students, no active halls,
  session not found) are shown as flash messages and the admin is returned
  to the exam list.

## Security

See `docs/user-guide.md` and the README's Security section for the full
list; in short: hashed passwords (Werkzeug `generate_password_hash`),
`@login_required` on every admin route, `secure_filename()` + extension
allow-list + `MAX_CONTENT_LENGTH` on uploads, uploaded files deleted
immediately after parsing (never kept on disk), and all secrets read from
environment variables via `.env` (never committed — see `.env.example`).
