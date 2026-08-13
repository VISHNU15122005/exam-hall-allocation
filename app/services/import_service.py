"""
Reads an uploaded Excel / CSV / PDF file and turns it into a list of
raw dict rows with normalized column names, ready for validation.

Raises ImportParseError with a user-safe message on failure.
"""
import os
import pandas as pd

COLUMN_ALIASES = {
    "register_number": [
        "register number", "register no", "reg no", "reg number",
        "registration number", "regno", "registernumber",
    ],
    "student_name": ["student name", "name", "studentname"],
    "subject": ["subject", "course", "paper"],
    "exam_date": ["exam date", "date", "examdate"],
    "exam_time": ["exam time", "time", "examtime"],
    "class_section": ["class", "section", "class/section", "class section"],
}

REQUIRED_LOGICAL_COLUMNS = ["register_number", "student_name", "subject", "exam_date", "exam_time"]


class ImportParseError(Exception):
    """User-facing, safe error message about a failed import."""
    pass


def _normalize_header(header: str) -> str:
    return str(header).strip().lower().replace("_", " ")


def _map_columns(columns):
    """Map raw file column names -> logical field names. Returns dict {raw_col: logical}."""
    mapping = {}
    for col in columns:
        norm = _normalize_header(col)
        matched = None
        for logical, aliases in COLUMN_ALIASES.items():
            if norm == logical.replace("_", " ") or norm in aliases:
                matched = logical
                break
        if matched:
            mapping[col] = matched
    return mapping


def _dataframe_to_rows(df: pd.DataFrame):
    if df.empty:
        raise ImportParseError("The uploaded file is empty. Please upload a file with student rows.")

    col_map = _map_columns(df.columns)
    missing = [c for c in REQUIRED_LOGICAL_COLUMNS if c not in col_map.values()]
    if missing:
        friendly = {
            "register_number": "Register Number",
            "student_name": "Student Name",
            "subject": "Subject",
            "exam_date": "Exam Date",
            "exam_time": "Exam Time",
        }
        missing_names = ", ".join(friendly[m] for m in missing)
        raise ImportParseError(
            f"Missing required column(s): {missing_names}. "
            f"Required columns are: Register Number, Student Name, Subject, Exam Date, Exam Time."
        )

    df = df.rename(columns=col_map)
    # keep only columns we understand, drop unrelated/unmapped columns
    keep_cols = [c for c in df.columns if c in REQUIRED_LOGICAL_COLUMNS + ["class_section"]]
    df = df[keep_cols]

    rows = []
    for _, r in df.iterrows():
        row = {c: (None if pd.isna(r[c]) else r[c]) for c in df.columns}
        # normalize date/time objects coming from Excel into strings the validator can parse
        for key in ("exam_date",):
            val = row.get(key)
            if hasattr(val, "strftime"):
                row[key] = val.strftime("%Y-%m-%d")
        for key in ("exam_time",):
            val = row.get(key)
            if hasattr(val, "strftime"):
                row[key] = val.strftime("%H:%M")
        rows.append(row)
    return rows


def parse_csv(filepath):
    try:
        df = pd.read_csv(filepath, dtype=str, keep_default_na=True)
    except pd.errors.EmptyDataError:
        raise ImportParseError("The uploaded CSV file is empty or unreadable.")
    except Exception:
        raise ImportParseError("The uploaded CSV file appears to be corrupted and could not be read.")
    return _dataframe_to_rows(df)


def parse_excel(filepath):
    try:
        df = pd.read_excel(filepath, dtype=str)
    except Exception:
        raise ImportParseError(
            "The uploaded Excel file appears to be corrupted or is not a valid .xlsx file."
        )
    return _dataframe_to_rows(df)


def parse_pdf(filepath):
    try:
        import pdfplumber
    except ImportError:
        raise ImportParseError("PDF import is not available on this server (pdfplumber not installed).")

    all_rows = []
    header_mapped = None
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    header = table[0]
                    col_map = _map_columns(header)
                    if header_mapped is None:
                        header_mapped = col_map
                    for row_cells in table[1:]:
                        row = {}
                        for raw_col, cell in zip(header, row_cells):
                            logical = col_map.get(raw_col)
                            if logical:
                                row[logical] = cell
                        if row:
                            all_rows.append(row)
    except Exception:
        raise ImportParseError(
            "Unable to extract student data from this PDF.\n\n"
            "Please ensure the PDF contains a readable table with:\n"
            "Register Number, Student Name, Subject, Exam Date, Exam Time."
        )

    if not all_rows:
        raise ImportParseError(
            "Unable to extract student data from this PDF.\n\n"
            "Please ensure the PDF contains a readable table with:\n"
            "Register Number, Student Name, Subject, Exam Date, Exam Time."
        )

    missing = [c for c in REQUIRED_LOGICAL_COLUMNS if c not in all_rows[0]]
    # check across all rows' keys combined, not just first row
    found_keys = set()
    for r in all_rows:
        found_keys.update(r.keys())
    missing = [c for c in REQUIRED_LOGICAL_COLUMNS if c not in found_keys]
    if missing:
        friendly = {
            "register_number": "Register Number", "student_name": "Student Name",
            "subject": "Subject", "exam_date": "Exam Date", "exam_time": "Exam Time",
        }
        raise ImportParseError(
            f"Missing required column(s) in PDF table: {', '.join(friendly[m] for m in missing)}."
        )

    return all_rows


def parse_file(filepath, filename):
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext == "csv":
        return parse_csv(filepath)
    elif ext == "xlsx":
        return parse_excel(filepath)
    elif ext == "pdf":
        return parse_pdf(filepath)
    else:
        raise ImportParseError(f"Unsupported file type: .{ext}. Please upload .xlsx, .csv or .pdf")
