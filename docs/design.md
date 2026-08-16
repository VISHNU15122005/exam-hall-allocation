# Tactive Assessment — System Design

## Exam Hall Allocation System

**Deliverable:** Detailed functional and technical design

---

## 1. Functional Requirements

### FR-01 — Authentication
An administrator must authenticate before accessing protected administrative functionality.

### FR-02 — Hall Management
The system must support hall creation and persistence, including capacity and associated seats.

### FR-03 — Student Import
The system must accept valid student data and create/persist the relevant exam-session/student records.

### FR-04 — Input Validation
Invalid or incomplete student data must be rejected with appropriate validation results.

### FR-05 — Allocation
Students must be assigned seats without exceeding available hall capacity.

### FR-06 — Multi-Hall Allocation
When one hall is insufficient, additional eligible halls can be used.

### FR-07 — Allocation Idempotency
Re-running allocation must not duplicate seats.

### FR-08 — Seating Plan
The system must render filled and empty seats accurately.

### FR-09 — Class/Section Adjacency
Students from the same Class/Section should not be seated next to each other whenever possible.

---

## 2. Business Rules

| ID | Business Rule | Design Response |
|---|---|---|
| BR-01 | Every valid student should receive a seat where capacity permits | Allocation iterates through available seats |
| BR-02 | Hall capacity must never be exceeded | Capacity guard |
| BR-03 | A seat cannot be assigned twice | Allocation state / persistence checks |
| BR-04 | Inactive halls are not used | Eligible-hall filtering |
| BR-05 | Allocation can span halls | Continue allocation across eligible halls |
| BR-06 | Re-running allocation must not duplicate seats | Idempotent allocation behavior |
| BR-07 | Invalid student data is rejected | Import validators |
| BR-08 | Duplicate register numbers in a session are rejected | Duplicate validation |
| BR-09 | Same-Class/Section adjacency is avoided when possible | Neighbor-aware seat selection |

---

## 3. Allocation Algorithm

### Input

```text
Students
Active halls
Available seats
Class/Section information
Existing allocation state
```

### Processing

```text
1. Preserve register-number order.
2. Obtain available seats.
3. For each student:
      a. Inspect free seats.
      b. Check same-row left/right neighbors.
      c. Prefer a seat with no same-Class/Section neighbor.
      d. If none exists, use the first remaining seat.
4. Continue until students are processed.
5. Use additional halls when required.
```

### Priority

```text
Priority 1: Seat the student
Priority 2: Do not exceed capacity
Priority 3: Do not duplicate a seat
Priority 4: Prefer non-adjacent same-Class/Section placement
```

The source report explicitly states that the adjacency preference yields to the requirement to seat everyone when no suitable non-adjacent seat exists.

---

## 4. Adjacency Logic

### Definition

Two seats are adjacent when:

```text
same hall
AND
same row
AND
abs(column1 - column2) == 1
```

### Example

```text
Row 1

S1   S2   S3   S4
│    │    │    │
└────┘    └────┘
 adjacent   adjacent
```

A student is preferred for a seat where the immediate left/right neighbor is not occupied by a student from the same Class/Section.

---

## 5. Import Design

### Required data categories evidenced by tests

- Register number
- Student name
- Subject
- Exam date
- Exam time
- Class/Section

### Validation sequence

```text
Upload
  ↓
Check file format
  ↓
Check required columns
  ↓
Read rows
  ↓
Validate required fields
  ↓
Validate date/time
  ↓
Validate register number
  ↓
Check duplicates
  ↓
Persist valid import
```

Invalid uploads should not be partially persisted in the tested failure paths.

---

## 6. Hall Design

Hall management supports:

- Hall creation
- Capacity
- Seat persistence
- Multiple independent halls
- Active/inactive state
- Exclusion of inactive halls during allocation

### Capacity boundaries

```text
Students == Capacity
        ↓
All students can be seated

Students > Capacity
        ↓
Extra student remains unallocated
        OR
Additional eligible hall is used
```

---

## 7. Exam Session Design

The system supports independent exam sessions.

The recorded test:

`test_multiple_independent_exam_sessions_reuse_same_halls_without_conflict`

demonstrates that the same halls can be reused for independent sessions without cross-session seating conflicts.

---

## 8. Seating Plan Design

The seating plan represents the resulting allocation.

The recorded test verifies:

- Correct filled-seat rendering
- Correct empty-seat rendering

The plan is therefore treated as a presentation of allocation state rather than as the source of business-rule enforcement.

---

## 9. Authentication Design

The verified authentication design includes:

- Password hashing via Werkzeug
- Login protection
- Admin-route protection
- Server-side authorization
- Ownership checks where relevant

The session confirms a manual flow:

```text
GET /login → 200
POST /login → authenticated
GET / → 200
Dashboard text present
```

---

## 10. Error Handling Design

The system has tested negative paths for:

- Missing student fields
- Invalid date/time
- Duplicate register number
- Invalid register-number characters
- Invalid file format
- Missing import columns
- Capacity boundaries
- Inactive halls

The design objective is to reject invalid operations before they create invalid persistent state.

---

## 11. Security Design

### Verified controls

| Area | Control |
|---|---|
| Passwords | Werkzeug hashing |
| Admin routes | `@login_required` |
| Uploads | secure filename/type/size checks |
| SQL injection | no raw `text()/execute()` matches found |
| XSS | no `|safe` / `Markup()` matches found |
| Environment secrets | `.env` ignored |

### Known gaps

- CSRF protection absent
- Debug mode enabled
- Insecure SECRET_KEY fallback
- No login rate limiting

---

## 12. Testability Design

The design intentionally exposes business rules through testable service behavior.

Test groups include:

- Allocation
- Adjacency
- Student import
- Validation
- Hall management
- Seating
- Authentication

The final verified unit suite reports:

**67 passed, 0 failed**

---

## 13. Change Impact

The adjacency feature affects:

- Allocation service
- Student Class/Section usage
- Allocation tests
- README
- Architecture documentation
- Design documentation
- User guide
- AI change-loop evidence

The recorded change loop confirms that the existing 60-test baseline remained green during Attempt 1.

---

## 14. Design Constraints

The source audit deliberately leaves some implementation details unspecified:

- Exact database engine
- Exact package versions
- Complete frontend framework details
- Full route inventory

These should be confirmed from the actual repository before presenting them as facts.
