from flask import Blueprint, render_template
from flask_login import login_required

from app.models import ExamSession, Allocation, Hall

seating_bp = Blueprint("seating", __name__, url_prefix="/seating")


@seating_bp.route("/<int:session_id>")
@login_required
def view_session(session_id):
    exam_session = ExamSession.query.get_or_404(session_id)
    allocations = Allocation.query.filter_by(exam_session_id=session_id).all()

    unallocated_count = exam_session.student_count - len(allocations)

    halls_used = {}
    for alloc in allocations:
        halls_used.setdefault(alloc.hall_id, {"hall": alloc.hall, "seats": {}})
        halls_used[alloc.hall_id]["seats"][alloc.seat.label] = alloc

    hall_grids = []
    for hall_id, info in halls_used.items():
        hall = info["hall"]
        grid = []
        for r in range(hall.rows):
            row_letter = chr(ord("A") + r)
            row_cells = []
            for c in range(1, hall.cols + 1):
                label = f"{row_letter}{c}"
                alloc = info["seats"].get(label)
                row_cells.append({"label": label, "allocation": alloc})
            grid.append(row_cells)
        hall_grids.append({"hall": hall, "grid": grid})

    return render_template(
        "seating.html",
        exam_session=exam_session,
        hall_grids=hall_grids,
        unallocated_count=max(unallocated_count, 0),
    )
