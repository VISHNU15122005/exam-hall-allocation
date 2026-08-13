import sys
import os
import datetime as dt

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db as _db
from app.models import Admin, ExamSession, Student, Hall


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "_uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"xlsx", "csv", "pdf"}


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin(db):
    a = Admin(username="admin")
    a.set_password("admin123")
    db.session.add(a)
    db.session.commit()
    return a


@pytest.fixture()
def exam_session(db):
    s = ExamSession(subject="Data Structures", exam_date=dt.date(2026, 8, 20),
                     exam_time=dt.time(10, 0))
    db.session.add(s)
    db.session.commit()
    return s


def make_students(db, session, count, prefix="23CSE"):
    students = []
    for i in range(1, count + 1):
        s = Student(register_number=f"{prefix}{i:03d}", student_name=f"Student {i}",
                    exam_session_id=session.id)
        db.session.add(s)
        students.append(s)
    db.session.commit()
    return students


def make_hall(db, name, code, rows, cols, active=True):
    h = Hall(name=name, code=code, rows=rows, cols=cols, is_active=active)
    db.session.add(h)
    db.session.commit()
    h.ensure_seats()
    return h
