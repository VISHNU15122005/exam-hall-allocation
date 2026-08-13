from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Hall

halls_bp = Blueprint("halls", __name__, url_prefix="/halls")


@halls_bp.route("/")
@login_required
def list_halls():
    halls = Hall.query.order_by(Hall.name).all()
    return render_template("halls.html", halls=halls)


@halls_bp.route("/create", methods=["POST"])
@login_required
def create_hall():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    try:
        rows = int(request.form.get("rows"))
        cols = int(request.form.get("cols"))
    except (TypeError, ValueError):
        flash("Rows and columns must be valid numbers.", "danger")
        return redirect(url_for("halls.list_halls"))

    if not name or not code:
        flash("Hall name and code are required.", "danger")
        return redirect(url_for("halls.list_halls"))
    if rows <= 0 or cols <= 0:
        flash("Rows and columns must be greater than zero.", "danger")
        return redirect(url_for("halls.list_halls"))
    if Hall.query.filter_by(code=code).first():
        flash(f"Hall code '{code}' already exists.", "danger")
        return redirect(url_for("halls.list_halls"))

    hall = Hall(name=name, code=code, rows=rows, cols=cols, is_active=True)
    db.session.add(hall)
    db.session.commit()
    hall.ensure_seats()
    flash(f"Hall '{name}' created with capacity {rows * cols}.", "success")
    return redirect(url_for("halls.list_halls"))


@halls_bp.route("/<int:hall_id>/toggle", methods=["POST"])
@login_required
def toggle_hall(hall_id):
    hall = Hall.query.get_or_404(hall_id)
    hall.is_active = not hall.is_active
    db.session.commit()
    flash(f"Hall '{hall.name}' is now {'active' if hall.is_active else 'inactive'}.", "info")
    return redirect(url_for("halls.list_halls"))
