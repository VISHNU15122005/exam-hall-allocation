from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Student, ExamSession, Hall, Allocation, ImportBatch

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    total_students = Student.query.count()
    total_sessions = ExamSession.query.count()
    active_halls = Hall.query.filter_by(is_active=True).count()
    allocated_students = Allocation.query.count()

    sessions = ExamSession.query.order_by(ExamSession.exam_date).limit(10).all()
    recent_imports = ImportBatch.query.order_by(ImportBatch.uploaded_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_sessions=total_sessions,
        active_halls=active_halls,
        allocated_students=allocated_students,
        sessions=sessions,
        recent_imports=recent_imports,
    )
