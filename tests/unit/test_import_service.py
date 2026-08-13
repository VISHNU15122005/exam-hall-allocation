"""
Unit tests for app.services.import_service (column mapping / parsing).
Uses real pandas DataFrames written to temp files - no Flask/DB dependency.
"""
import os
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.import_service import parse_csv, parse_excel, ImportParseError


def _write_csv(rows, columns):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)
    return path


def _write_xlsx(rows, columns):
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    pd.DataFrame(rows, columns=columns).to_excel(path, index=False)
    return path


def test_valid_csv_is_parsed():
    path = _write_csv(
        [["23CSE001", "Arun Kumar", "Data Structures", "2026-08-20", "10:00 AM"]],
        ["Register Number", "Student Name", "Subject", "Exam Date", "Exam Time"],
    )
    rows = parse_csv(path)
    os.remove(path)
    assert len(rows) == 1
    assert rows[0]["register_number"] == "23CSE001"


def test_column_alias_variants_are_normalized():
    path = _write_csv(
        [["23CSE002", "Divya Raj", "OS", "2026-08-21", "2:00 PM"]],
        ["Reg No", "Name", "Subject", "Date", "Time"],
    )
    rows = parse_csv(path)
    os.remove(path)
    assert rows[0]["register_number"] == "23CSE002"
    assert rows[0]["student_name"] == "Divya Raj"


def test_missing_required_column_raises_import_error():
    path = _write_csv(
        [["23CSE003", "No Time Col", "OS", "2026-08-21"]],
        ["Register Number", "Student Name", "Subject", "Exam Date"],
    )
    try:
        parse_csv(path)
        raised = False
    except ImportParseError:
        raised = True
    os.remove(path)
    assert raised is True


def test_empty_csv_raises_import_error():
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w") as f:
        f.write("Register Number,Student Name,Subject,Exam Date,Exam Time\n")
    try:
        parse_csv(path)
        raised = False
    except ImportParseError:
        raised = True
    os.remove(path)
    assert raised is True


def test_valid_xlsx_is_parsed():
    path = _write_xlsx(
        [["23CSE004", "Karthik Iyer", "Data Structures", "2026-08-20", "10:00 AM"]],
        ["Register Number", "Student Name", "Subject", "Exam Date", "Exam Time"],
    )
    rows = parse_excel(path)
    os.remove(path)
    assert len(rows) == 1
    assert rows[0]["student_name"] == "Karthik Iyer"


def test_unrelated_extra_columns_are_dropped_not_accepted():
    path = _write_csv(
        [["23CSE005", "Meena", "OS", "2026-08-21", "2:00 PM", "some junk"]],
        ["Register Number", "Student Name", "Subject", "Exam Date", "Exam Time", "Unrelated Column"],
    )
    rows = parse_csv(path)
    os.remove(path)
    assert "Unrelated Column" not in rows[0]
    assert "unrelated_column" not in rows[0]
