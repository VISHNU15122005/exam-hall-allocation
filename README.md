# AI-Assisted Exam Hall & Seat Allocation System

**Automated Student Data Import, Intelligent Seating Allocation & AI-Driven QA**

Built for the Tactive AI-Powered QA Automation, Documentation & Software
Engineering Assessment.

## Problem

A college exam administrator needs to take a raw student exam list
(Excel/CSV/PDF) and turn it into a valid hall-and-seat allocation, with no
double-bookings, no capacity overruns, and a clear record of anything that
couldn't be seated.

## Solution

A single Flask web app: upload → validate → preview → confirm → group into
exam sessions → configure halls → auto-allocate seats → visual seating
plan → search → export. See `docs/architecture.md` and `docs/design.md`
for the full breakdown.

## Features

- Excel / CSV / PDF student list import with column-alias normalization
- Full validation (missing fields, bad dates/times, duplicates, corrupt/empty/
  unsupported files) with a preview step — nothing is saved without admin
  confirmation
- Automatic grouping into exam sessions (Subject + Date + Time)
- Hall management (capacity, rows × columns, active/inactive)
- Allocation engine enforcing 8 business rules (see `docs/design.md`)
- Interactive click-to-inspect seating grid
- Student search by register number / name
- Excel and PDF export of the seating plan
- Admin authentication with hashed passwords

## Architecture

```
exam-hall-allocation/
├── app/
│   ├── routes/        # Flask blueprints (thin controllers)
│   ├── services/       # import parsing + allocation engine
│   ├── validators/     # row/batch validation rules
│   ├── models.py        # SQLAlchemy models
│   ├── templates/, static/
├── tests/
│   ├── unit/            # pytest - validator, import parser, allocation engine
│   └── integration/     # Playwright e2e workflow test
├── docs/                 # architecture, design, user guide, test strategy, AI change loop
├── sample_data/           # valid + deliberately invalid sample files
├── scripts/generate_sample_data.py
├── run.py, config.py, requirements.txt
```

Full detail: `docs/architecture.md`.

## Technology Stack

Backend: Python + Flask · DB: SQLite + SQLAlchemy · Frontend: Bootstrap 5 +
Jinja (server-rendered, no SPA) · File processing: pandas, openpyxl,
pdfplumber · Export: openpyxl, reportlab · Testing: pytest, Playwright

Reasoning for each choice is in `docs/architecture.md`.

## Installation

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd exam-hall-allocation

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# edit .env and set a real SECRET_KEY
```

## Database Setup

No manual step needed — `create_app()` calls `db.create_all()` on startup
and seeds one demo admin (`admin` / `admin123`) if no admin exists yet.
To create additional/production admins:

```bash
flask --app run.py create-admin <username> <password>
```

## Running the Application

```bash
python run.py
```

Visit `http://127.0.0.1:5000`, log in with `admin` / `admin123`.

## Sample Data

```bash
python scripts/generate_sample_data.py
```

Regenerates everything in `sample_data/`:

- `students.xlsx`, `students.csv` — 40 valid records across 2 exam
  sessions (Data Structures / Operating Systems) — this is the intended
  **demo dataset**: create 2 halls of 20 seats each to see allocation
  span both halls.
- `students.pdf` — 15 valid records in a readable table, for testing PDF
  import.
- `invalid_students.xlsx` — one row per validation rule (missing register
  number, missing name, missing subject, invalid date, invalid time, and
  an intra-file duplicate register number) — for testing the preview
  screen's error reporting.

These files (and the parsing/validation logic that reads them) were
regenerated and verified for real while building this repo — see
`docs/test-strategy.md` for the actual output captured.

## Input File Format

Required columns (common header variants like "Reg No" / "Name" / "Date"
are auto-normalized — see `COLUMN_ALIASES` in
`app/services/import_service.py`):

```
Register Number | Student Name | Subject | Exam Date | Exam Time
```

Optional: `Class/Section` (used only by the not-yet-implemented adjacency
seating rule — see `docs/ai-change-loop.md`).

## Allocation Rules

1. Every student receives exactly one seat
2. One seat belongs to only one student
3. Hall capacity is never exceeded
4. A student is never allocated twice for the same session
5. Duplicate register numbers are rejected at import
6. Only students in the selected session are allocated
7. If capacity is short, unallocated students are reported with a reason
8. A student can't be double-booked at the exact same date/time across
   different sessions

Full mapping of rule → code in `docs/design.md`.

## Running Tests

```bash
pytest tests/unit -v
```

Covers: row/batch validation, file parsing/column normalization, and all
8 allocation business rules (normal/edge/invalid cases — see
`docs/test-strategy.md` for the full coverage table).

## Running Playwright

```bash
pip install playwright
playwright install
python run.py &          # app must be running
pytest tests/integration/test_e2e_workflow.py
```

## Security

- Passwords hashed with Werkzeug (`generate_password_hash`)
- Every admin route protected with `@login_required`
- Uploaded files: extension allow-list (`.xlsx`/`.csv`/`.pdf`), 10 MB
  limit, `secure_filename()`, deleted immediately after parsing (never
  persisted to disk)
- User-facing errors are always specific and safe — never a raw stack
  trace
- Secrets read from environment variables (`.env`, never committed —
  `.env.example` provided)
- `.gitignore` excludes `venv/`, `__pycache__/`, `*.db`, `uploads/*`, `.env`

## AI Tools Used

```
Claude (Anthropic)
- Application implementation (routes, services, validators, models)
- Test generation (pytest unit tests)
- Documentation (architecture, design, user guide, test strategy)
```

*(Update this section to reflect every AI tool you actually used, e.g. if
you additionally used ChatGPT for planning or ran the AI change loop with
Claude Code — see `docs/ai-change-loop.md`.)*

## AI Testing

19 of the delivered unit tests (validator + file parser — the parts with
no Flask dependency) were actually executed while building this repo, in a
sandboxed environment with no network access, and passed 19/19. The
remaining tests (allocation engine, Playwright e2e) are written and
syntax-checked but need a real `pip install` to execute — do that first,
then run `pytest tests/unit -v` yourself and keep the real output for your
submission. Full honesty notes: `docs/test-strategy.md`.

## Deliberate Red Run

Not yet performed against a live pytest run (this build environment had no
network access to install Flask-SQLAlchemy/pytest). `docs/test-strategy.md`
gives the exact one-line bug to introduce, the command to run, and the
expected failing test — do this yourself and capture the real output for
your submission, then revert and confirm green again.



