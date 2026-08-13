# User Guide (for the Exam Administrator)

1. **Login** — go to `/login`, sign in with your admin username/password
   (demo: `admin` / `admin123`).
2. **Upload** — from the sidebar, click *Upload Data*. Choose an `.xlsx`,
   `.csv` or `.pdf` file containing Register Number, Student Name, Subject,
   Exam Date and Exam Time columns (common header variants like "Reg No" or
   "Name" are recognized automatically).
3. **Review the preview** — every row is shown with a Valid/Invalid badge
   and, for invalid rows, the exact reason (missing field, bad date, bad
   time, duplicate). Use the filter box to find specific rows. Nothing is
   saved yet.
4. **Fix errors** — if there are errors you want corrected, fix the source
   file and re-upload. There is no in-browser row editor in this version.
5. **Confirm import** — click *Confirm & Save*. Only valid rows are written
   to the database; students are automatically grouped into examination
   sessions by Subject + Date + Time.
6. **Configure halls** — go to *Halls*, add each hall with a name, code,
   rows and columns (capacity = rows × columns). Toggle a hall
   active/inactive to include or exclude it from allocation.
7. **Select an exam** — go to *Exam Sessions* to see every session with its
   student count and allocation status.
8. **Generate allocation** — click *Generate Allocation* on a session card.
   The system fills active halls with students and reports how many were
   seated vs. left unallocated (if capacity is short).
9. **View seating** — click *View Seating Plan* for a visual hall grid;
   click any occupied seat to see the student's full details in a popup.
10. **Search a student** — go to *Student Search*, search by register number
    or name to see their subject, date, time, hall and seat in one card.
11. **Export results** — from the seating plan page, download the complete
    hall-wise seating arrangement as Excel or PDF.
