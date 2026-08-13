"""
Allocation engine.

Given an ExamSession, assigns every enrolled Student to a unique
(Hall, Seat) combination, respecting:

  Rule 1: Every student receives exactly one seat.
  Rule 2: One seat belongs to only one student (per session).
  Rule 3: Hall capacity cannot be exceeded.
  Rule 4: A student cannot be allocated twice for the same session.
  Rule 6: Only students belonging to the selected session are allocated.
  Rule 7: If capacity is insufficient, unallocated students are reported.
  Rule 8: A student must not already be allocated to another exam at the
          exact same date/time.

NOTE: adjacency-by-class/section spacing (the "AI change loop" feature)
is intentionally NOT implemented in this version - see docs/ai-change-loop.md.
"""
from app.extensions import db
from app.models import Student, Hall, Allocation, ExamSession


class AllocationError(Exception):
    pass


def get_active_halls():
    return Hall.query.filter_by(is_active=True).order_by(Hall.name).all()


def _student_has_conflicting_allocation(student: Student, session: ExamSession) -> bool:
    """Rule 8: same student, same date & time, different session already allocated."""
    conflict = (
        db.session.query(Allocation)
        .join(ExamSession, Allocation.exam_session_id == ExamSession.id)
        .join(Student, Allocation.student_id == Student.id)
        .filter(
            Student.register_number == student.register_number,
            ExamSession.exam_date == session.exam_date,
            ExamSession.exam_time == session.exam_time,
            ExamSession.id != session.id,
        )
        .first()
    )
    return conflict is not None


def generate_allocation(exam_session_id: int, reset_existing: bool = False):
    """
    Allocates all students of the given exam session to available halls/seats.

    Returns a dict:
      {
        "allocated": [Allocation, ...],
        "unallocated": [Student, ...],   # e.g. capacity shortfall / time conflict
        "total_students": int,
        "total_capacity": int,
      }
    """
    session = ExamSession.query.get(exam_session_id)
    if session is None:
        raise AllocationError("Examination session not found.")

    if reset_existing:
        Allocation.query.filter_by(exam_session_id=session.id).delete()
        db.session.commit()

    already_allocated_ids = {
        a.student_id for a in Allocation.query.filter_by(exam_session_id=session.id).all()
    }

    students = session.students.order_by(Student.register_number).all()
    if not students:
        raise AllocationError("This exam session has no students to allocate.")

    halls = get_active_halls()
    if not halls:
        raise AllocationError("No active halls are available. Please add or activate a hall first.")

    total_capacity = sum(h.capacity for h in halls)

    # build the pool of free (hall, seat) slots not already used in this session
    used_seat_ids = {
        a.seat_id for a in Allocation.query.filter_by(exam_session_id=session.id).all()
    }
    free_slots = []
    for hall in halls:
        hall.ensure_seats()
        for seat in hall.seats.order_by("row_label", "col_number").all():
            if seat.id not in used_seat_ids:
                free_slots.append((hall, seat))

    allocated = []
    unallocated = []
    slot_index = 0

    for student in students:
        if student.id in already_allocated_ids:
            continue  # Rule 4: never allocate the same student twice

        if _student_has_conflicting_allocation(student, session):
            unallocated.append({
                "student": student,
                "reason": "Student already has another exam scheduled at this exact date/time.",
            })
            continue

        if slot_index >= len(free_slots):
            unallocated.append({
                "student": student,
                "reason": "Insufficient hall capacity.",
            })
            continue

        hall, seat = free_slots[slot_index]
        slot_index += 1

        allocation = Allocation(
            student_id=student.id,
            exam_session_id=session.id,
            hall_id=hall.id,
            seat_id=seat.id,
            seat_label=seat.label,
        )
        db.session.add(allocation)
        allocated.append(allocation)

    db.session.commit()

    return {
        "allocated": allocated,
        "unallocated": unallocated,
        "total_students": len(students),
        "total_capacity": total_capacity,
    }
