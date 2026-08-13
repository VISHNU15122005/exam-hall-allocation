"""
Validates a single normalized student row (a dict) coming from an
uploaded Excel / CSV / PDF file.

A row looks like:
{
    "register_number": "23CSE001",
    "student_name": "Arun Kumar",
    "subject": "Data Structures",
    "exam_date": "2026-08-20",   # raw string as read from file
    "exam_time": "10:00 AM",     # raw string as read from file
    "class_section": "CSE-A",    # optional
}

Returns (is_valid: bool, errors: list[str], normalized: dict|None)
"""
import datetime as dt
import re

REQUIRED_FIELDS = ["register_number", "student_name", "subject", "exam_date", "exam_time"]

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y", "%d %b %Y", "%m/%d/%Y"]
TIME_FORMATS = ["%I:%M %p", "%H:%M", "%I %p", "%H:%M:%S"]


def _clean(value):
    if value is None:
        return ""
    return str(value).strip()


def parse_date(raw):
    raw = _clean(raw)
    if not raw:
        return None
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_time(raw):
    raw = _clean(raw)
    if not raw:
        return None
    raw_norm = re.sub(r"\s+", " ", raw.upper().replace(".", ""))
    for fmt in TIME_FORMATS:
        try:
            return dt.datetime.strptime(raw_norm, fmt).time()
        except ValueError:
            continue
    return None


def validate_row(row: dict, row_number: int = None):
    errors = []

    register_number = _clean(row.get("register_number"))
    student_name = _clean(row.get("student_name"))
    subject = _clean(row.get("subject"))
    exam_date_raw = row.get("exam_date")
    exam_time_raw = row.get("exam_time")
    class_section = _clean(row.get("class_section")) or None

    if not register_number:
        errors.append("Missing register number")
    elif not re.match(r"^[A-Za-z0-9\-_/]{2,30}$", register_number):
        errors.append("Register number contains invalid characters")

    if not student_name:
        errors.append("Missing student name")
    elif len(student_name) > 150:
        errors.append("Student name is too long")

    if not subject:
        errors.append("Missing subject")

    parsed_date = parse_date(exam_date_raw)
    if not _clean(exam_date_raw):
        errors.append("Missing exam date")
    elif parsed_date is None:
        errors.append(f"Invalid exam date: '{exam_date_raw}'")

    parsed_time = parse_time(exam_time_raw)
    if not _clean(exam_time_raw):
        errors.append("Missing exam time")
    elif parsed_time is None:
        errors.append(f"Invalid exam time: '{exam_time_raw}'")

    is_valid = len(errors) == 0
    normalized = None
    if is_valid:
        normalized = {
            "register_number": register_number,
            "student_name": student_name,
            "subject": subject,
            "exam_date": parsed_date,
            "exam_time": parsed_time,
            "class_section": class_section,
        }
    return is_valid, errors, normalized


def validate_batch(rows: list):
    """
    Validate a full list of raw rows.
    Detects duplicate register numbers WITHIN the same exam session
    (same subject + date + time), since a student can legitimately sit
    for several different exams.

    Returns a list of result dicts, one per input row, each with:
    row_number, status ('valid'|'invalid'), errors, normalized
    """
    results = []
    seen_keys = {}  # (register_number, subject, date, time) -> first row_number

    if len(rows) == 0:
        return results

    for idx, row in enumerate(rows, start=1):
        is_valid, errors, normalized = validate_row(row, idx)

        if is_valid:
            key = (
                normalized["register_number"].upper(),
                normalized["subject"].strip().lower(),
                normalized["exam_date"],
                normalized["exam_time"],
            )
            if key in seen_keys:
                is_valid = False
                errors = [
                    f"Duplicate register number for this exam "
                    f"(also appears in row {seen_keys[key]})"
                ]
            else:
                seen_keys[key] = idx

        results.append({
            "row_number": idx,
            "status": "valid" if is_valid else "invalid",
            "errors": errors,
            "normalized": normalized,
            "raw": row,
        })

    return results
