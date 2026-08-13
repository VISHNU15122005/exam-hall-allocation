import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app, session
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Student, ExamSession, ImportBatch
from app.services.import_service import parse_file, ImportParseError
from app.validators.student_validator import validate_batch

imports_bp = Blueprint("imports", __name__, url_prefix="/imports")

# Server-side, in-memory holding area for preview results before confirmation.
# Keyed by a random token so nothing is ever auto-saved to the DB on upload.
_PREVIEW_CACHE = {}


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@imports_bp.route("/", methods=["GET"])
@login_required
def upload_form():
    return render_template("import_upload.html")


@imports_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("imports.upload_form"))

    if not _allowed_file(file.filename):
        flash("Unsupported file type. Please upload .xlsx, .csv or .pdf", "danger")
        return redirect(url_for("imports.upload_form"))

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file.save(filepath)

    try:
        raw_rows = parse_file(filepath, filename)
    except ImportParseError as e:
        flash(str(e), "danger")
        return redirect(url_for("imports.upload_form"))
    finally:
        # don't keep uploaded files around longer than needed for parsing
        if os.path.exists(filepath):
            os.remove(filepath)

    results = validate_batch(raw_rows)
    token = uuid.uuid4().hex
    _PREVIEW_CACHE[token] = {"filename": filename, "results": results}
    session["preview_token"] = token
    return redirect(url_for("imports.preview"))


@imports_bp.route("/preview")
@login_required
def preview():
    token = session.get("preview_token")
    data = _PREVIEW_CACHE.get(token)
    if not data:
        flash("No pending import to preview. Please upload a file first.", "warning")
        return redirect(url_for("imports.upload_form"))

    results = data["results"]
    valid_count = sum(1 for r in results if r["status"] == "valid")
    invalid_count = len(results) - valid_count

    return render_template(
        "import_preview.html",
        filename=data["filename"],
        results=results,
        total=len(results),
        valid_count=valid_count,
        invalid_count=invalid_count,
    )


@imports_bp.route("/confirm", methods=["POST"])
@login_required
def confirm():
    token = session.get("preview_token")
    data = _PREVIEW_CACHE.get(token)
    if not data:
        flash("Nothing to confirm. Please upload a file first.", "warning")
        return redirect(url_for("imports.upload_form"))

    results = data["results"]
    valid_rows = [r for r in results if r["status"] == "valid"]

    batch = ImportBatch(
        filename=data["filename"],
        total_rows=len(results),
        valid_rows=len(valid_rows),
        invalid_rows=len(results) - len(valid_rows),
        admin_id=current_user.id,
    )
    db.session.add(batch)
    db.session.flush()

    saved = 0
    skipped_existing = 0
    for r in valid_rows:
        n = r["normalized"]
        exam_session = ExamSession.query.filter_by(
            subject=n["subject"], exam_date=n["exam_date"], exam_time=n["exam_time"]
        ).first()
        if not exam_session:
            exam_session = ExamSession(
                subject=n["subject"], exam_date=n["exam_date"], exam_time=n["exam_time"]
            )
            db.session.add(exam_session)
            db.session.flush()

        exists = Student.query.filter_by(
            register_number=n["register_number"], exam_session_id=exam_session.id
        ).first()
        if exists:
            skipped_existing += 1
            continue

        student = Student(
            register_number=n["register_number"],
            student_name=n["student_name"],
            class_section=n["class_section"],
            exam_session_id=exam_session.id,
            import_batch_id=batch.id,
        )
        db.session.add(student)
        saved += 1

    db.session.commit()
    _PREVIEW_CACHE.pop(token, None)
    session.pop("preview_token", None)

    msg = f"Import confirmed: {saved} student record(s) saved."
    if skipped_existing:
        msg += f" {skipped_existing} record(s) already existed and were skipped."
    flash(msg, "success")
    return redirect(url_for("dashboard.index"))
