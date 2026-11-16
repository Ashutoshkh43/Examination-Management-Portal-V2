from datetime import date, time

from flask import Blueprint, request
from flask_security import auth_required, current_user, roles_required

from controllers.database import db
from models.models import (
    Booking,
    Evaluation,
    Examination,
    Examiner,
    ExaminerAssignment,
    ExaminationSlot
)

examiner_bp = Blueprint('examiner', __name__)


def get_current_examiner():
    return Examiner.query.filter_by(user_id=current_user.id).first()


def get_booked_count(slot_id):
    return Booking.query.filter(
        Booking.slot_id == slot_id,
        Booking.status != 'Cancelled'
    ).count()


def get_pending_evaluation_count(examination_id=None, examiner_id=None):
    query = db.session.query(Booking).join(
        ExaminationSlot, Booking.slot_id == ExaminationSlot.id
    ).outerjoin(
        Evaluation, Evaluation.booking_id == Booking.id
    ).filter(
        Booking.status != 'Cancelled',
        Evaluation.id.is_(None)
    )

    if examination_id is not None:
        query = query.filter(ExaminationSlot.examination_id == examination_id)
    if examiner_id is not None:
        query = query.filter(ExaminationSlot.examiner_id == examiner_id)

    return query.count()


@examiner_bp.get('/dashboard')
@auth_required('token')
@roles_required('examiner')
def examiner_dashboard():
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    assignments = ExaminerAssignment.query.filter_by(
        examiner_id=examiner.id, status='active'
    ).all()
    slots = ExaminationSlot.query.filter_by(examiner_id=examiner.id).all()

    total_booked_students = sum(get_booked_count(slot.id) for slot in slots)
    pending_evaluations = get_pending_evaluation_count(examiner_id=examiner.id)

    return {
        'role': 'examiner',
        'stats': {
            'assigned_examinations': len(assignments),
            'total_slots': len(slots),
            'booked_students': total_booked_students,
            'pending_evaluations': pending_evaluations
        }
    }, 200


@examiner_bp.get('/examinations')
@auth_required('token')
@roles_required('examiner')
def get_assigned_examinations():
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    assignments = ExaminerAssignment.query.filter_by(
        examiner_id=examiner.id, status='active'
    ).all()

    examinations = []
    for assignment in assignments:
        examination = assignment.examination
        exam_slots = ExaminationSlot.query.filter_by(
            examination_id=examination.id, examiner_id=examiner.id
        ).all()

        slot_dates = [slot.date for slot in exam_slots]
        date_range = '-'
        if slot_dates:
            date_range = f'{min(slot_dates).isoformat()} to {max(slot_dates).isoformat()}'

        examinations.append({
            'id': examination.id,
            'examination_name': examination.examination_name,
            'course_code': examination.course.course_code,
            'course_name': examination.course.course_name,
            'examination_type': examination.examination_type,
            'duration': examination.duration,
            'maximum_marks': examination.maximum_marks,
            'status': examination.status,
            'date_range': date_range,
            'slot_creation_start': examination.slot_creation_start.isoformat() if examination.slot_creation_start else None,
            'slot_creation_end': examination.slot_creation_end.isoformat() if examination.slot_creation_end else None,
            'slot_count': len(exam_slots)
        })

    return {'examinations': examinations}, 200


@examiner_bp.get('/slots')
@auth_required('token')
@roles_required('examiner')
def get_examiner_slots():
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    slots = ExaminationSlot.query.filter_by(examiner_id=examiner.id).order_by(
        ExaminationSlot.date, ExaminationSlot.start_time
    ).all()

    return {
        'slots': [
            {
                'id': slot.id,
                'examination_id': slot.examination_id,
                'examination_name': slot.examination.examination_name,
                'course_code': slot.examination.course.course_code,
                'date': slot.date.isoformat(),
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'capacity': slot.maximum_student_capacity,
                'available_seats': slot.available_seats,
                'booked_count': get_booked_count(slot.id),
                'status': 'Full' if slot.status != 'Cancelled' and slot.available_seats <= 0 else slot.status,
                'meeting_link': slot.meeting_link
            }
            for slot in slots
        ]
    }, 200


@examiner_bp.get('/slots/<int:slot_id>/students')
@auth_required('token')
@roles_required('examiner')
def get_slot_students(slot_id):
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    slot = ExaminationSlot.query.filter_by(id=slot_id, examiner_id=examiner.id).first()
    if not slot:
        return {'message': 'Slot not found or not assigned to you.'}, 404

    bookings = Booking.query.filter(
        Booking.slot_id == slot.id, Booking.status != 'Cancelled'
    ).all()

    students = []
    for booking in bookings:
        student = booking.student
        evaluation = Evaluation.query.filter_by(booking_id=booking.id).first()

        students.append({
            'booking_id': booking.id,
            'student_id': student.id,
            'student_name': student.fullname,
            'registration_number': student.registration_number,
            'department': student.department,
            'semester': student.semester,
            'booking_status': booking.status,
            'evaluation_status': evaluation.status if evaluation else 'Pending',
            'total_marks': evaluation.total_marks if evaluation else None
        })

    return {
        'slot': {
            'id': slot.id,
            'examination_name': slot.examination.examination_name,
            'date': slot.date.isoformat(),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M')
        },
        'students': students
    }, 200


@examiner_bp.post('/slots')
@auth_required('token')
@roles_required('examiner')
def create_examiner_slot():
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    data = request.get_json(silent=True) or {}

    try:
        examination_id = int(data.get('examination_id'))
        capacity = int(data.get('capacity'))
        slot_date = date.fromisoformat(str(data.get('date') or ''))
        start_time = time.fromisoformat(str(data.get('start_time') or ''))
        end_time = time.fromisoformat(str(data.get('end_time') or ''))
    except (TypeError, ValueError):
        return {'message': 'Enter a valid examination, date, time, and capacity.'}, 400

    if capacity < 1:
        return {'message': 'Capacity must be greater than zero.'}, 400
    if start_time >= end_time:
        return {'message': 'End time must be later than start time.'}, 400

    examination = db.session.get(Examination, examination_id)
    if not examination:
        return {'message': 'Examination not found.'}, 404
    if examination.status != 'Slot Creation':
        return {'message': 'Slot creation is not open for this examination.'}, 400

    assignment = ExaminerAssignment.query.filter_by(
        examination_id=examination.id, examiner_id=examiner.id, status='active'
    ).first()
    if not assignment:
        return {'message': 'You are not assigned to this examination.'}, 403

    conflict = ExaminationSlot.query.filter(
        ExaminationSlot.examiner_id == examiner.id,
        ExaminationSlot.date == slot_date,
        ExaminationSlot.status != 'Cancelled',
        ExaminationSlot.start_time < end_time,
        ExaminationSlot.end_time > start_time
    ).first()
    if conflict:
        return {'message': 'You already have a slot during this time.'}, 409

    meeting_link = str(data.get('meeting_link') or '').strip()
    if len(meeting_link) > 500:
        return {'message': 'Meeting link must be 500 characters or fewer.'}, 400

    slot = ExaminationSlot(
        examination_id=examination.id,
        examiner_id=examiner.id,
        date=slot_date,
        start_time=start_time,
        end_time=end_time,
        maximum_student_capacity=capacity,
        available_seats=capacity,
        meeting_link=meeting_link or None,
        status='Available'
    )

    db.session.add(slot)
    db.session.commit()

    return {'message': 'Examination slot created successfully.', 'slot_id': slot.id}, 201


@examiner_bp.patch('/examinations/<int:examination_id>/complete')
@auth_required('token')
@roles_required('examiner')
def mark_examination_completed(examination_id):
    examiner = get_current_examiner()
    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    examination = db.session.get(Examination, examination_id)
    if not examination:
        return {'message': 'Examination not found.'}, 404

    assignment = ExaminerAssignment.query.filter_by(
        examination_id=examination.id, examiner_id=examiner.id, status='active'
    ).first()
    if not assignment:
        return {'message': 'You are not assigned to this examination.'}, 403

    if examination.status == 'Completed':
        return {'message': 'This examination is already completed.'}, 400

    pending_count = get_pending_evaluation_count(examination_id=examination.id)
    if pending_count > 0:
        return {
            'message': (
                f'{pending_count} student evaluation(s) are still pending. '
                'Complete those evaluations before marking the examination as completed.'
            )
        }, 400

    examination.status = 'Completed'

    exam_slots = ExaminationSlot.query.filter_by(
        examination_id=examination.id
    ).filter(ExaminationSlot.status != 'Cancelled').all()

    for slot in exam_slots:
        slot.status = 'Completed'

    db.session.commit()
    return {'message': 'Examination marked as completed successfully.'}, 200


@examiner_bp.get('/bookings')
@auth_required('token')
@roles_required('examiner')
def get_examiner_bookings():
    examiner = get_current_examiner()

    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    bookings = db.session.query(Booking).join(
        ExaminationSlot,
        Booking.slot_id == ExaminationSlot.id
    ).filter(
        ExaminationSlot.examiner_id == examiner.id,
        Booking.status != 'Cancelled'
    ).order_by(
        ExaminationSlot.date.desc(),
        ExaminationSlot.start_time.desc()
    ).all()

    students = []

    for booking in bookings:
        slot = booking.slot
        student = booking.student
        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id
        ).first()

        students.append({
            'booking_id': booking.id,
            'student_id': student.id,
            'student_name': student.fullname,
            'registration_number': student.registration_number,
            'slot': (
                f'{slot.date.isoformat()} '
                f'{slot.start_time.strftime("%H:%M")}-'
                f'{slot.end_time.strftime("%H:%M")}'
            ),
            'slot_date': slot.date.isoformat(),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'examination_name': slot.examination.examination_name,
            'booking_status': booking.status,
            'evaluation_status': (
                evaluation.status if evaluation else 'Pending'
            ),
            'total_marks': evaluation.total_marks if evaluation else None
        })

    return {
        'students': students
    }, 200

@examiner_bp.get('/profile')
@auth_required('token')
@roles_required('examiner')
def get_examiner_profile():

    examiner = get_current_examiner()

    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    return {
        'profile': {
            'id': examiner.id,
            'fullname': examiner.fullname,
            'employee_id': examiner.employee_id,
            'email': current_user.email,
            'department': examiner.department,
            'designation': examiner.designation
        }
    }, 200


@examiner_bp.put('/profile')
@auth_required('token')
@roles_required('examiner')
def update_examiner_profile():

    examiner = get_current_examiner()

    if not examiner:
        return {'message': 'Examiner profile not found.'}, 404

    data = request.get_json(silent=True) or {}

    fullname = str(data.get('fullname') or '').strip()
    department = str(data.get('department') or '').strip()
    designation = str(data.get('designation') or '').strip()

    if not fullname:
        return {'message': 'Full name is required.'}, 400

    if not department:
        return {'message': 'Department is required.'}, 400

    if not designation:
        return {'message': 'Designation is required.'}, 400

    examiner.fullname = fullname
    examiner.department = department
    examiner.designation = designation

    db.session.commit()

    return {
        'message': 'Profile updated successfully.',
        'profile': {
            'id': examiner.id,
            'fullname': examiner.fullname,
            'employee_id': examiner.employee_id,
            'email': current_user.email,
            'department': examiner.department,
            'designation': examiner.designation
        }
    }, 200