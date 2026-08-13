# Architecture

## System Overview

A single Flask application (server-rendered, Bootstrap 5 UI) backed by SQLite.
No separate frontend build step, no microservices — one process, one database,
kept deliberately simple per the assessment brief.

```
Browser (Bootstrap/JS)
        │  HTTP
        ▼
Flask app (Blueprints per feature)
        │
   ┌────┴─────────────────────┐
   │ routes/  (thin controllers)
   │ services/ (business logic: import parsing, allocation engine)
   │ validators/ (row-level validation rules)
   │ models.py (SQLAlchemy ORM)
   └────┬─────────────────────┘
        ▼
   SQLite (exam_hall.db)
```

## Components

- **routes/** – one Flask Blueprint per feature area (auth, dashboard,
  imports, halls, exams, allocation, seating, search, export). Routes only
  handle HTTP concerns (form parsing, redirects, flash messages) and delegate
  everything else.
- **services/import_service.py** – reads `.xlsx` / `.csv` (pandas) and `.pdf`
  (pdfplumber table extraction), normalizes column headers via an alias map,
  and returns raw row dicts. Raises `ImportParseError` with a user-safe
  message on any failure (empty file, corrupt file, missing columns,
  unreadable PDF table).
- **validators/student_validator.py** – pure functions, no DB or Flask
  dependency. `validate_row()` checks one row; `validate_batch()` also
  detects duplicate register numbers within the same exam session. This
  separation is what let core logic be unit-tested in isolation.
- **services/allocation_service.py** – the allocation engine. Loads a
  session's students and active halls' free seats, then assigns
  (hall, seat) pairs in register-number order, enforcing all 8 business
  rules (see `docs/design.md`).
- **models.py** – SQLAlchemy models: `Admin`, `ExamSession`, `Student`,
  `Hall`, `Seat`, `Allocation`, `ImportBatch`. Database-level unique
  constraints back up the application-level rules (e.g. a student can't be
  allocated twice per session, a seat can't be double-booked).

## Data Flow (Import → Allocation)

```
Upload file
    → import_service.parse_file()      (extract raw rows)
    → student_validator.validate_batch() (validate + flag duplicates)
    → import_preview.html               (admin reviews, nothing saved yet)
    → imports.confirm()                 (only valid rows persisted)
    → ExamSession grouping (subject + date + time)
    → halls.create_hall() / activation  (admin configures halls)
    → allocation_service.generate_allocation()
    → seating.view_session()            (visual grid, click-to-inspect)
    → export.export_excel() / export_pdf()
```

## Technology Choices

| Concern | Choice | Reason |
|---|---|---|
| Backend | Flask | Small surface area, explicit routing, easy to test, no build tooling |
| DB | SQLite + SQLAlchemy | Zero-config, ships with the repo, constraints still enforced |
| Frontend | Server-rendered Jinja + Bootstrap 5 | No SPA complexity needed for an admin-facing CRUD/allocation tool |
| Excel | pandas + openpyxl | De-facto standard, robust dtype/NaN handling |
| PDF import | pdfplumber | Reliable table extraction from text-based PDFs without OCR |
| PDF export | reportlab | Fine-grained control over the seating-plan table layout |
| Testing | pytest (unit/integration) + Playwright (e2e) | Matches assessment requirement; Playwright drives the real browser workflow |

## Why not React / microservices / etc.

The brief explicitly asks for a simple, explainable stack. A single Flask
app with server-rendered templates is enough to deliver every required
feature (dashboard, upload, preview, allocation, seating grid, search,
export) without the operational overhead of a separate API + SPA build.
