
from datetime import datetime, date

from flask import Blueprint
from flask_security import auth_required, current_user, roles_required

from controllers.database import db
from models.models import Student, Examination, ExaminationSlot, Booking

student_bp = Blueprint('student', __name__)


@student_bp.get('/dashboard')
@auth_required('token')
@roles_required('student')
def student_dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()

    if not student:
        return {'message': 'Student profile not found.'}, 404

    today = date.today()

    total_examinations = Examination.query.count()

    # Count examinations that are open for booking
    available_examinations = Examination.query.filter_by(
        status='Booking Open'
    ).count()

    my_bookings = Booking.query.filter_by(
        student_id=student.id
    ).filter(
        Booking.status != 'Cancelled'
    ).count()

    upcoming_examinations = Booking.query.join(
        ExaminationSlot,
        Booking.slot_id == ExaminationSlot.id
    ).filter(
        Booking.student_id == student.id,
        Booking.status == 'Booked',
        ExaminationSlot.date >= today
    ).count()

    published_results = db.session.query(
        Examination.id
    ).join(
        Booking,
        Booking.examination_id == Examination.id
    ).filter(
        Booking.student_id == student.id,
        Booking.status != 'Cancelled',
        Examination.results_published.is_(True)
    ).distinct().count()

    return {
        'role': 'student',
        'dashboard': 'Student Dashboard',
        'message': 'Welcome Student',
        'stats': {
            'total_examinations': total_examinations,
            'available_examinations': available_examinations,
            'my_bookings': my_bookings,
            'upcoming_examinations': upcoming_examinations,
            'published_results': published_results
        }
    }, 200
