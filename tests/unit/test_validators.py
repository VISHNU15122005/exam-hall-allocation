"""
Unit tests for app.validators.student_validator.
No Flask/DB dependency - runs standalone.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.validators.student_validator import validate_row, validate_batch


VALID_ROW = {
    "register_number": "23CSE001",
    "student_name": "Arun Kumar",
    "subject": "Data Structures",
    "exam_date": "20-Aug-2026",
    "exam_time": "10:00 AM",
}


def test_valid_row_passes():
    ok, errors, normalized = validate_row(VALID_ROW)
    assert ok is True
    assert errors == []
    assert normalized["register_number"] == "23CSE001"


def test_missing_register_number_is_rejected():
    row = dict(VALID_ROW, register_number="")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("register number" in e.lower() for e in errors)


def test_missing_student_name_is_rejected():
    row = dict(VALID_ROW, student_name="")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("student name" in e.lower() for e in errors)


def test_missing_subject_is_rejected():
    row = dict(VALID_ROW, subject="")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("subject" in e.lower() for e in errors)


def test_missing_exam_date_is_rejected():
    row = dict(VALID_ROW, exam_date="")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("exam date" in e.lower() for e in errors)


def test_invalid_exam_date_is_rejected():
    row = dict(VALID_ROW, exam_date="32-13-2026")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("invalid exam date" in e.lower() for e in errors)


def test_missing_exam_time_is_rejected():
    row = dict(VALID_ROW, exam_time="")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("exam time" in e.lower() for e in errors)


def test_invalid_exam_time_is_rejected():
    row = dict(VALID_ROW, exam_time="99:99 XY")
    ok, errors, _ = validate_row(row)
    assert ok is False
    assert any("invalid exam time" in e.lower() for e in errors)


def test_alternate_date_and_time_formats_are_accepted():
    row = dict(VALID_ROW, exam_date="2026-08-20", exam_time="14:00")
    ok, errors, normalized = validate_row(row)
    assert ok is True
    assert normalized["exam_date"].isoformat() == "2026-08-20"


def test_duplicate_register_number_within_same_session_is_rejected():
    rows = [VALID_ROW, dict(VALID_ROW)]  # exact duplicate: same reg no + subject + date + time
    results = validate_batch(rows)
    assert results[0]["status"] == "valid"
    assert results[1]["status"] == "invalid"
    assert any("duplicate" in e.lower() for e in results[1]["errors"])


def test_same_register_number_different_subject_is_allowed():
    row2 = dict(VALID_ROW, subject="Operating Systems", exam_time="02:00 PM")
    results = validate_batch([VALID_ROW, row2])
    assert results[0]["status"] == "valid"
    assert results[1]["status"] == "valid"


def test_empty_batch_returns_empty_results():
    assert validate_batch([]) == []


def test_register_number_with_invalid_characters_is_rejected():
    row = dict(VALID_ROW, register_number="23CSE 001!!")
    ok, errors, _ = validate_row(row)
    assert ok is False


TESTS = [v for k, v in list(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    passed, failed = 0, 0
    for t in TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
