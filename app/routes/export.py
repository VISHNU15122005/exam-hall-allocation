import io

from flask import Blueprint, send_file, abort
from flask_login import login_required
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.models import ExamSession, Allocation

export_bp = Blueprint("export", __name__, url_prefix="/export")

HEADERS = ["Register Number", "Student Name", "Subject", "Date", "Time", "Hall", "Seat"]


def _rows_for_session(exam_session):
    allocations = (
        Allocation.query.filter_by(exam_session_id=exam_session.id)
        .order_by(Allocation.hall_id, Allocation.seat_label)
        .all()
    )
    rows = []
    for a in allocations:
        rows.append([
            a.student.register_number,
            a.student.student_name,
            exam_session.subject,
            exam_session.exam_date.strftime("%d-%b-%Y"),
            exam_session.exam_time.strftime("%I:%M %p"),
            a.hall.name,
            a.seat_label,
        ])
    return rows


@export_bp.route("/<int:session_id>/excel")
@login_required
def export_excel(session_id):
    exam_session = ExamSession.query.get_or_404(session_id)
    rows = _rows_for_session(exam_session)
    if not rows:
        abort(404, "No allocation found for this exam session yet.")

    wb = Workbook()
    ws = wb.active
    ws.title = "Seating Plan"
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    for col_cells in ws.columns:
        length = max(len(str(c.value)) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = length + 4

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"seating_plan_{exam_session.subject}_{exam_session.exam_date}.xlsx".replace(" ", "_")
    return send_file(buf, as_attachment=True, download_name=filename,
                      mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@export_bp.route("/<int:session_id>/pdf")
@login_required
def export_pdf(session_id):
    exam_session = ExamSession.query.get_or_404(session_id)
    rows = _rows_for_session(exam_session)
    if not rows:
        abort(404, "No allocation found for this exam session yet.")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"Seating Plan — {exam_session.subject}", styles["Title"]),
        Paragraph(
            f"{exam_session.exam_date.strftime('%d-%b-%Y')} at "
            f"{exam_session.exam_time.strftime('%I:%M %p')}",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]
    table_data = [HEADERS] + rows
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2749")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f4fa")]),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)

    filename = f"seating_plan_{exam_session.subject}_{exam_session.exam_date}.pdf".replace(" ", "_")
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")
