# Tactive Assessment — System Architecture

## Exam Hall Allocation System

**Deliverable:** Architecture documentation

---

## 1. System Overview

The Exam Hall Allocation System is a Flask-based web application for managing examination halls, importing student records, generating seat allocations, and displaying seating plans.

The recorded project contains:

- 9 route blueprints
- 2 service modules
- 1 validator module
- `models.py`
- Student import and validation
- Hall management
- Allocation service
- Seating-plan rendering
- Authentication
- Automated tests
- One Playwright integration/E2E test

---

## 2. High-Level Architecture

```text
+-------------------------------------------------------------+
|                        ADMIN / USER                          |
|                                                             |
| Login | Upload Students | Manage Halls | Generate Seating  |
+-------------------------------+-----------------------------+
                                |
                                | HTTP
                                v
+-------------------------------------------------------------+
|                    FLASK WEB APPLICATION                    |
|                                                             |
| Authentication | Route Blueprints | Validation | Admin APIs |
+-------------------------------+-----------------------------+
                                |
                                v
+-------------------------------------------------------------+
|                       SERVICE LAYER                         |
|                                                             |
| Student Import | Allocation Service | Validation Logic     |
+-------------------------------+-----------------------------+
                                |
                                v
+-------------------------------------------------------------+
|                     MODEL / DATA LAYER                      |
|                                                             |
|                    SQLAlchemy / Models                      |
|                                                             |
| Student | Exam Session | Hall | Seat | Allocation | ...    |
+-------------------------------+-----------------------------+
                                |
                                v
+-------------------------------------------------------------+
|                         DATABASE                            |
|                                                             |
|              Exact database engine not stated               |
+-------------------------------------------------------------+
```

The exact database engine is intentionally not named because the source session did not verify it.

---

## 3. Presentation Layer

The application exposes a browser-facing workflow for an administrator.

The recorded README workflow is:

```text
Login
 ↓
Upload student data
 ↓
Preview
 ↓
Confirm
 ↓
Manage halls
 ↓
Generate allocation
 ↓
View seating
 ↓
Search
 ↓
Export
```

The exact frontend framework/template/CSS implementation was not fully enumerated in the QA audit, so this document avoids asserting a framework that was not verified.

---

## 4. Application Layer

Flask is the evidenced web framework.

The source session reports 9 route blueprints and confirms that the application uses:

- Authentication routes
- Student/import routes
- Hall routes
- Allocation routes
- Seating routes
- Admin functionality
- Validation
- Authorization

The backend receives requests, authenticates users, validates input, applies allocation rules, interacts with the data layer and returns pages or responses.

---

## 5. Service Layer

Two service modules are evidenced in the project.

The allocation service is particularly important because it contains the seat-allocation logic.

Its responsibilities include:

1. Selecting eligible halls.
2. Respecting hall capacity.
3. Avoiding duplicate seats.
4. Supporting multiple halls.
5. Preserving allocation behavior across independent exam sessions.
6. Applying Class/Section adjacency preference.
7. Falling back to a normal free seat when adjacency avoidance is impossible.

---

## 6. Allocation Architecture

### Standard allocation

```text
Students
   ↓
Validate student records
   ↓
Get active halls
   ↓
Get available seats
   ↓
Allocate student
   ↓
Continue across halls if necessary
   ↓
Generate seating plan
```

### Adjacency-aware allocation

```text
Student
   ↓
Inspect free seats
   ↓
Check left/right same-row neighbors
   ↓
Same Class/Section neighbor?
   ├── NO → preferred seat
   └── YES → try another seat
                 ↓
        No preferred seat left?
                 ↓
          fallback free seat
```

The fallback is intentional: seating everyone has higher priority than the adjacency preference.

---

## 7. Adjacency Definition

The recorded feature defines adjacency as:

- Same hall
- Same row
- Column difference exactly 1

Therefore:

```text
Hall A, Row 1:
[ A1 ] [ A2 ] [ A3 ] [ A4 ]

A1 ↔ A2  adjacent
A2 ↔ A3  adjacent
A3 ↔ A4  adjacent

Hall A Row 1 ↔ Hall A Row 2
not adjacent

Hall A ↔ Hall B
not adjacent
```

---

## 8. Data Architecture

The design documentation was cross-checked against a **seven-table data model**. The audit does not reproduce every table name, so the architecture intentionally describes the data responsibilities rather than inventing exact schema names.

Core concepts evidenced include:

- Students
- Exam sessions
- Halls
- Seats
- Allocations / seating assignments
- Authentication/user data
- Supporting relational records

Relationships support:

```text
Exam Session
     |
     +---- Students
     |
     +---- Halls
              |
              +---- Seats
                     |
                     +---- Allocation
```

---

## 9. Import Architecture

Student import supports the tested validation path for:

- Required fields
- Class/Section
- Register number
- Student name
- Subject
- Exam date
- Exam time
- Duplicate detection
- File format
- Required-column validation

The source session explicitly confirms that the Class/Section field now feeds the adjacency feature.

---

## 10. Authentication and Authorization

The recorded security review confirms:

- Password hashing via Werkzeug
- `@login_required` on admin routes
- Admin authentication
- Server-side authorization
- Ownership checks for sensitive operations

The session only explicitly evidences an administrator role. A separate student authorization model is not claimed unless supported by the source.

---

## 11. Technology Stack

| Technology / Component | Role | Evidence |
|---|---|---|
| Python | Application and test runtime | venv, pip, pytest |
| Flask | Web application framework | routes/blueprints and `app.run` |
| Werkzeug | Password hashing | security review |
| pytest | Automated test framework | recorded test commands |
| SQLAlchemy | Model/data layer | project/test evidence |
| Playwright | Browser integration/E2E | integration test file |

Not verified: exact package versions, exact database engine, complete frontend technology list and hosting platform.

---

## 12. Test Architecture

```text
tests/
├── unit/
│   ├── validators
│   ├── import service
│   ├── allocation service
│   ├── auth routes
│   ├── halls routes
│   ├── imports routes
│   └── seating routes
│
└── integration/
    └── test_e2e_workflow.py
```

The unit suite contains the primary verified coverage.

The integration/E2E test exists but was not successfully executed in the recorded sandbox.

---

## 13. Security Architecture

### Verified

- Password hashing
- Protected admin routes
- Secure upload filename handling
- File type allow-list
- File size limit
- Temporary upload deletion
- No raw SQL execution patterns found
- No unsafe template output patterns found
- `.env` excluded

### Open

- CSRF protection
- Debug mode
- Secret-key fallback
- Login rate limiting

---

## 14. Deployment Evidence

The project includes a production-style WSGI start reference:

```text
gunicorn app:app
```

The exact production hosting platform was not verified in the QA session.

---

## 15. Architecture Principles

The recorded implementation reflects:

1. Server-side business-rule enforcement.
2. Separation of route and service responsibilities.
3. Automated regression testing.
4. Explicit validation before persistence.
5. Allocation logic that protects capacity.
6. Feature additions that preserve existing behavior.
7. Evidence-driven AI-assisted iteration.
