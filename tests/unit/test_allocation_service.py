"""
Tests for app.services.allocation_service - the core business rules.
Requires the full stack (Flask-SQLAlchemy); run with:
    pytest tests/unit/test_allocation_service.py
"""
import datetime as dt

import pytest

from app.services.allocation_service import generate_allocation, AllocationError
from app.models import Allocation, Student, ExamSession
from tests.conftest import make_students, make_hall


def test_each_student_receives_exactly_one_seat(db, exam_session):
    students = make_students(db, exam_session, 10)
    make_hall(db, "Hall A", "HALL-A", rows=4, cols=4)  # capacity 16

    result = generate_allocation(exam_session.id)

    assert len(result["allocated"]) == 10
    assert result["unallocated"] == []
    allocations = Allocation.query.filter_by(exam_session_id=exam_session.id).all()
    student_ids = [a.student_id for a in allocations]
    assert len(student_ids) == len(set(student_ids))  # each student appears once


def test_allocation_never_exceeds_hall_capacity(db, exam_session):
    make_students(db, exam_session, 20)
    make_hall(db, "Hall A", "HALL-A", rows=3, cols=3)  # capacity 9

    result = generate_allocation(exam_session.id)

    allocated_count = len(result["allocated"])
    assert allocated_count <= 9
    assert allocated_count == 9
    assert len(result["unallocated"]) == 11


def test_same_seat_is_never_given_to_two_students(db, exam_session):
    make_students(db, exam_session, 12)
    make_hall(db, "Hall A", "HALL-A", rows=4, cols=4)

    result = generate_allocation(exam_session.id)

    seat_ids = [a.seat_id for a in result["allocated"]]
    assert len(seat_ids) == len(set(seat_ids))


def test_insufficient_capacity_reports_unallocated_students(db, exam_session):
    make_students(db, exam_session, 5)
    make_hall(db, "Hall A", "HALL-A", rows=1, cols=2)  # capacity 2

    result = generate_allocation(exam_session.id)

    assert len(result["allocated"]) == 2
    assert len(result["unallocated"]) == 3
    reasons = [u["reason"] for u in result["unallocated"]]
    assert all("capacity" in r.lower() for r in reasons)


def test_allocation_spans_multiple_halls_when_needed(db, exam_session):
    make_students(db, exam_session, 15)
    make_hall(db, "Hall A", "HALL-A", rows=2, cols=5)  # 10
    make_hall(db, "Hall B", "HALL-B", rows=2, cols=5)  # 10

    result = generate_allocation(exam_session.id)

    assert len(result["allocated"]) == 15
    halls_used = {a.hall_id for a in result["allocated"]}
    assert len(halls_used) == 2


def test_inactive_halls_are_not_used(db, exam_session):
    make_students(db, exam_session, 5)
    make_hall(db, "Hall A", "HALL-A", rows=2, cols=2, active=False)  # inactive, cap 4

    with pytest.raises(AllocationError):
        generate_allocation(exam_session.id)


def test_generate_allocation_without_students_raises_error(db):
    session = ExamSession(subject="Empty Subject", exam_date=dt.date(2026, 9, 1),
                           exam_time=dt.time(9, 0))
    db.session.add(session)
    db.session.commit()
    make_hall(db, "Hall A", "HALL-A", rows=2, cols=2)

    with pytest.raises(AllocationError):
        generate_allocation(session.id)


def test_re_running_allocation_does_not_duplicate_seats(db, exam_session):
    make_students(db, exam_session, 5)
    make_hall(db, "Hall A", "HALL-A", rows=3, cols=3)

    generate_allocation(exam_session.id)
    result_2 = generate_allocation(exam_session.id)  # re-run without reset

    # already-allocated students are skipped, not re-allocated to a new seat
    assert len(result_2["allocated"]) == 0
    all_allocs = Allocation.query.filter_by(exam_session_id=exam_session.id).all()
    assert len(all_allocs) == 5


def test_student_cannot_have_two_exams_at_same_date_time(db):
    date, time = dt.date(2026, 8, 20), dt.time(10, 0)
    session_a = ExamSession(subject="Data Structures", exam_date=date, exam_time=time)
    session_b = ExamSession(subject="Operating Systems", exam_date=date, exam_time=time)
    db.session.add_all([session_a, session_b])
    db.session.commit()

    # same register number enrolled in both sessions at the identical date/time
    s1 = Student(register_number="23CSE900", student_name="Clash Student",
                 exam_session_id=session_a.id)
    s2 = Student(register_number="23CSE900", student_name="Clash Student",
                 exam_session_id=session_b.id)
    db.session.add_all([s1, s2])
    db.session.commit()

    make_hall(db, "Hall A", "HALL-A", rows=2, cols=2)

    generate_allocation(session_a.id)  # allocates s1 first
    result_b = generate_allocation(session_b.id)  # s2 should be blocked by Rule 8

    assert len(result_b["unallocated"]) == 1
    assert "already has another exam" in result_b["unallocated"][0]["reason"].lower()
