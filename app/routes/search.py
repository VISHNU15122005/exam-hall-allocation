from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models import Student, Allocation

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/")
@login_required
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        students = (
            Student.query.filter(
                (Student.register_number.ilike(f"%{query}%"))
                | (Student.student_name.ilike(f"%{query}%"))
            )
            .limit(50)
            .all()
        )
        for s in students:
            alloc = Allocation.query.filter_by(student_id=s.id).first()
            results.append({"student": s, "allocation": alloc})
    return render_template("search.html", query=query, results=results)
