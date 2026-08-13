from flask import Blueprint, render_template
from flask_login import login_required

from app.models import ExamSession

exams_bp = Blueprint("exams", __name__, url_prefix="/exams")


@exams_bp.route("/")
@login_required
def list_exams():
    sessions = ExamSession.query.order_by(ExamSession.exam_date, ExamSession.exam_time).all()
    return render_template("exams.html", sessions=sessions)
