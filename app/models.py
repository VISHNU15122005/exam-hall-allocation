import datetime as dt

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class ExamSession(db.Model):
    """A unique Subject + Date + Time combination."""

    __tablename__ = "exam_sessions"
    __table_args__ = (
        db.UniqueConstraint("subject", "exam_date", "exam_time", name="uq_session"),
    )

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.Time, nullable=False)

    students = db.relationship("Student", backref="exam_session", lazy="dynamic")
    allocations = db.relationship("Allocation", backref="exam_session", lazy="dynamic")

    @property
    def student_count(self):
        return self.students.count()

    @property
    def is_allocated(self):
        return self.allocations.count() > 0


class Student(db.Model):
    __tablename__ = "students"
    __table_args__ = (
        db.UniqueConstraint(
            "register_number", "exam_session_id", name="uq_student_session"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(50), nullable=False, index=True)
    student_name = db.Column(db.String(150), nullable=False)
    class_section = db.Column(db.String(50), nullable=True)  # used by adjacency rule
    exam_session_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False)
    import_batch_id = db.Column(db.Integer, db.ForeignKey("import_batches.id"), nullable=True)

    allocation = db.relationship("Allocation", backref="student", uselist=False)

    @property
    def subject(self):
        return self.exam_session.subject

    @property
    def exam_date(self):
        return self.exam_session.exam_date

    @property
    def exam_time(self):
        return self.exam_session.exam_time


class Hall(db.Model):
    __tablename__ = "halls"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    seats = db.relationship("Seat", backref="hall", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def capacity(self):
        return self.rows * self.cols

    def ensure_seats(self):
        """Create Seat rows for this hall if not already present."""
        if self.seats.count() > 0:
            return
        for r in range(self.rows):
            row_letter = chr(ord("A") + r)
            for c in range(1, self.cols + 1):
                seat = Seat(hall_id=self.id, row_label=row_letter, col_number=c,
                            label=f"{row_letter}{c}")
                db.session.add(seat)
        db.session.commit()


class Seat(db.Model):
    __tablename__ = "seats"
    __table_args__ = (
        db.UniqueConstraint("hall_id", "label", name="uq_hall_seat_label"),
    )

    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey("halls.id"), nullable=False)
    row_label = db.Column(db.String(5), nullable=False)
    col_number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(10), nullable=False)


class Allocation(db.Model):
    __tablename__ = "allocations"
    __table_args__ = (
        # Rule: one student gets exactly one seat per exam session
        db.UniqueConstraint("student_id", "exam_session_id", name="uq_alloc_student_session"),
        # Rule: one seat cannot be given to two students in the same session
        db.UniqueConstraint("exam_session_id", "hall_id", "seat_id", name="uq_alloc_seat_session"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    exam_session_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey("halls.id"), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"), nullable=False)
    seat_label = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    hall = db.relationship("Hall")
    seat = db.relationship("Seat")


class ImportBatch(db.Model):
    __tablename__ = "import_batches"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    total_rows = db.Column(db.Integer, default=0)
    valid_rows = db.Column(db.Integer, default=0)
    invalid_rows = db.Column(db.Integer, default=0)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)

    students = db.relationship("Student", backref="import_batch", lazy="dynamic")
