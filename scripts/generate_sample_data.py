"""
Generates sample_data/*.xlsx / .csv / .pdf files used for manual testing,
automated tests and the assessment demo.

Run:  python scripts/generate_sample_data.py
"""
import os
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "sample_data")
os.makedirs(BASE, exist_ok=True)

FIRST_NAMES = ["Arun", "Divya", "Karthik", "Meena", "Suresh", "Priya", "Vignesh", "Anitha",
               "Ramesh", "Kavya", "Prasanna", "Lavanya", "Dinesh", "Swathi", "Manoj", "Deepa",
               "Ganesh", "Nisha", "Bharath", "Sowmya"]
LAST_NAMES = ["Kumar", "Raj", "Prasad", "Ravi", "Krishnan", "Iyer", "Murthy", "Devi",
              "Narayan", "Sundaram"]

SUBJECTS = [("Data Structures", "2026-08-20", "10:00 AM"), ("Operating Systems", "2026-08-21", "02:00 PM")]


def build_students(n, reg_prefix="23CSE"):
    rows = []
    for i in range(1, n + 1):
        subject, date, time = SUBJECTS[(i - 1) // 20 % len(SUBJECTS)]
        rows.append({
            "Register Number": f"{reg_prefix}{i:03d}",
            "Student Name": f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[i % len(LAST_NAMES)]}",
            "Subject": subject,
            "Exam Date": date,
            "Exam Time": time,
            "Class/Section": "CSE-A" if i % 2 == 0 else "CSE-B",
        })
    return rows


def main():
    # Demo dataset: 40 students across 2 halls (see sample_data/README for hall setup)
    demo_rows = build_students(40)
    df = pd.DataFrame(demo_rows)
    df.to_excel(os.path.join(BASE, "students.xlsx"), index=False)
    df.to_csv(os.path.join(BASE, "students.csv"), index=False)
    print("Wrote students.xlsx and students.csv (40 valid records)")

    # Invalid sample file: deliberately broken rows for validation testing
    invalid_rows = [
        {"Register Number": "", "Student Name": "No RegNo Student", "Subject": "Data Structures",
         "Exam Date": "2026-08-20", "Exam Time": "10:00 AM"},
        {"Register Number": "23CSE050", "Student Name": "", "Subject": "Data Structures",
         "Exam Date": "2026-08-20", "Exam Time": "10:00 AM"},
        {"Register Number": "23CSE051", "Student Name": "Missing Subject", "Subject": "",
         "Exam Date": "2026-08-20", "Exam Time": "10:00 AM"},
        {"Register Number": "23CSE052", "Student Name": "Bad Date", "Subject": "Data Structures",
         "Exam Date": "32-13-2026", "Exam Time": "10:00 AM"},
        {"Register Number": "23CSE053", "Student Name": "Bad Time", "Subject": "Data Structures",
         "Exam Date": "2026-08-20", "Exam Time": "25:99"},
        {"Register Number": "23CSE054", "Student Name": "Original Row", "Subject": "Data Structures",
         "Exam Date": "2026-08-20", "Exam Time": "10:00 AM"},
        {"Register Number": "23CSE054", "Student Name": "Duplicate Of Row Above", "Subject": "Data Structures",
         "Exam Date": "2026-08-20", "Exam Time": "10:00 AM"},
    ]
    pd.DataFrame(invalid_rows).to_excel(os.path.join(BASE, "invalid_students.xlsx"), index=False)
    print("Wrote invalid_students.xlsx (deliberately invalid rows)")

    # PDF sample using reportlab table (readable, extractable table)
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors

    pdf_rows = build_students(15, reg_prefix="23CSE1")
    header = ["Register Number", "Student Name", "Subject", "Exam Date", "Exam Time"]
    data = [header] + [[r["Register Number"], r["Student Name"], r["Subject"], r["Exam Date"], r["Exam Time"]]
                        for r in pdf_rows]
    doc = SimpleDocTemplate(os.path.join(BASE, "students.pdf"), pagesize=A4)
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2749")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    doc.build([table])
    print("Wrote students.pdf (15 valid records, readable table)")


if __name__ == "__main__":
    main()
