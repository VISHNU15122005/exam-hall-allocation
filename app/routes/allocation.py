from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required

from app.services.allocation_service import generate_allocation, AllocationError

allocation_bp = Blueprint("allocation", __name__, url_prefix="/allocation")


@allocation_bp.route("/generate/<int:session_id>", methods=["POST"])
@login_required
def generate(session_id):
    try:
        result = generate_allocation(session_id)
    except AllocationError as e:
        flash(str(e), "danger")
        return redirect(url_for("exams.list_exams"))

    flash(
        f"Allocation complete: {len(result['allocated'])} of "
        f"{result['total_students']} students allocated"
        + (f", {len(result['unallocated'])} unallocated." if result["unallocated"] else "."),
        "success" if not result["unallocated"] else "warning",
    )
    return redirect(url_for("seating.view_session", session_id=session_id))
