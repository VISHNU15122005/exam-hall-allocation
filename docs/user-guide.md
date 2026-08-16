# Exam Hall Allocation System — User Guide

## Tactive Assessment

A non-technical guide for an administrator operating the Exam Hall Allocation System.

---

## 1. Purpose

The application helps an administrator:

1. Log in securely.
2. Upload student records.
3. Validate and confirm student data.
4. Manage examination halls.
5. Generate seat allocations.
6. View the seating plan.
7. Search/export results where supported.

---

## 2. Login

Open the application login page.

The recorded session verified the demo administrator credentials:

```text
Username: admin
Password: admin123
```

These credentials are documented as demo-only and must not be treated as production credentials.

After successful login, the dashboard should be accessible.

---

## 3. Student Import

### Step 1 — Upload

Select the student data file.

### Step 2 — Preview

Review the imported records before confirmation.

### Step 3 — Validate

The system checks:

- Register number
- Student name
- Subject
- Exam date
- Exam time
- Class/Section
- Required columns
- Duplicate register numbers
- File format

### Step 4 — Confirm

Valid data is persisted to the exam-session/student records.

---

## 4. Class/Section Column

The Class/Section value is now used by the seating allocation feature.

Its purpose is to help prevent students from the same Class/Section from being seated next to one another.

The system treats the immediate left/right seat in the same row as adjacent.

---

## 5. Manage Halls

The hall-management workflow supports:

- Creating a hall
- Setting capacity
- Creating/persisting seats
- Managing multiple halls
- Excluding inactive halls

### Hall availability

An inactive hall is not considered for new allocation.

---

## 6. Generate Allocation

After valid students and halls are available:

1. Select/create the exam session.
2. Start allocation.
3. The system checks available halls and seats.
4. Students are assigned seats.
5. Additional halls can be used when necessary.
6. The seating plan is generated.

---

## 7. Seating Rules

The system enforces several important rules.

### Capacity

A hall must never be exceeded.

### Duplicate seats

The same seat cannot be assigned to multiple students.

### Multiple halls

If one hall is insufficient, allocation can continue into additional eligible halls.

### Re-running

Re-running the allocation should not duplicate seats.

### Class/Section adjacency

The system first prefers a free seat that does not place a student next to another student from the same Class/Section.

If no such seat is available, the system falls back to a free seat so the student can still be seated.

---

## 8. View Seating Plan

The seating plan displays the result of the allocation.

The automated suite verifies both:

- Filled seats
- Empty seats

This helps an administrator inspect the final hall arrangement.

---

## 9. Common Import Problems

### Missing register number

The row is rejected.

### Missing student name

The row is rejected.

### Missing subject

The row is rejected.

### Missing exam date/time

The row is rejected.

### Invalid date/time

The row is rejected.

### Duplicate register number

The duplicate is rejected within the relevant exam session.

### Invalid file format

The upload is rejected and the tested path confirms that nothing is saved.

### Missing required column

The upload is rejected.

---

## 10. Capacity Problems

If there are more students than available seats:

- The system must not exceed capacity.
- An additional eligible hall may be used.
- If there is still insufficient capacity, the excess student remains unallocated according to the tested boundary behavior.

---

## 11. Troubleshooting

### Login does not work

Check the administrator credentials and confirm that the application server is running.

### Student import fails

Check the required columns and required fields.

### Allocation does not use a hall

Check whether the hall is active and has available capacity.

### Same-Class/Section students appear adjacent

The adjacency rule is a preference, not an absolute constraint. When no non-adjacent seat is available, seating the student takes priority.

### Browser E2E test does not run

The recorded QA session could not execute Playwright because of the sandbox's browser/network limitations. This is an environment limitation, not a documented application failure.

---

## 12. Administrator Demo Flow

For a short demonstration:

```text
1. Login
2. Upload student file
3. Preview / confirm
4. Show hall management
5. Generate allocation
6. Open seating plan
7. Explain Class/Section adjacency
8. Run pytest
9. Show deliberate RED result
10. Restore code
11. Show final GREEN result
```

---

## 13. Final Verified Test State

The recorded fresh-environment unit run reached:

```text
67 passed, 0 failed
```

The broader run included the unverified Playwright integration test and reported:

```text
1 failed, 67 passed, 229 warnings
```

---

## 14. Important Note

This guide reflects the behavior evidenced in the QA report. UI labels, screenshots and exact visual layouts should be checked against the current application before a final submission.
