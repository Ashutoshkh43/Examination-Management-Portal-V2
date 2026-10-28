
from flask import Blueprint, request, current_app
from flask_security import auth_required, roles_required, utils

from controllers.database import db

from models.models import (
    User,
    Course,
    Examination,
    Student,
    Examiner,
    ExaminationSlot,
    Booking
)


admin_bp = Blueprint('admin', __name__)


def get_datastore():
    return current_app.extensions['security'].datastore


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@admin_bp.route('/dashboard', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_dashboard():

    return {
        'role': 'admin',

        'total_courses': Course.query.count(),

        'total_examinations': Examination.query.count(),

        'total_students': Student.query.count(),

        'total_examiners': Examiner.query.count(),

        'total_slots': ExaminationSlot.query.count(),

        'total_bookings': Booking.query.count(),

        'recent_activities': [],

        'examination_statuses': [],

        'booking_statuses': []
    }, 200


# --------------------------------------------------
# GET ALL EXAMINERS
# --------------------------------------------------

@admin_bp.route('/examiners', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_examiners():

    examiners = Examiner.query.order_by(
        Examiner.id.desc()
    ).all()

    return {
        'examiners': [
            {
                'id': examiner.id,

                'fullname': examiner.fullname,

                'email': examiner.user.email,

                'employee_id': examiner.employee_id,

                'contact': examiner.contact,

                'department': examiner.department,

                'designation': examiner.designation,

                'status': examiner.user.status,

                'assigned_examinations': 0
            }
            for examiner in examiners
        ]
    }, 200


# --------------------------------------------------
# CREATE EXAMINER
# --------------------------------------------------

@admin_bp.route('/examiners', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_examiner():

    data = request.get_json(silent=True) or {}

    fullname = str(data.get('fullname') or '').strip()

    email = str(data.get('email') or '').strip().lower()

    password = data.get('password', '')

    employee_id = str(
        data.get('employee_id') or ''
    ).strip()

    contact = str(
        data.get('contact') or ''
    ).strip()

    department = str(
        data.get('department') or ''
    ).strip()

    designation = str(
        data.get('designation') or ''
    ).strip()

    if (
        not fullname
        or not email
        or not isinstance(password, str)
        or not password
        or not employee_id
    ):
        return {
            'message': (
                'Full name, email, password and employee ID '
                'are required.'
            )
        }, 400

    if len(password) < 8:
        return {
            'message': 'Password must contain at least 8 characters.'
        }, 400

    if User.query.filter_by(email=email).first():
        return {
            'message': 'An account with this email already exists.'
        }, 409

    if Examiner.query.filter_by(
        employee_id=employee_id
    ).first():
        return {
            'message': 'This employee ID already exists.'
        }, 409

    datastore = get_datastore()

    examiner_role = datastore.find_role('examiner')

    if not examiner_role:
        return {
            'message': 'Examiner role is not configured.'
        }, 500

    # Hash the password before saving it.
    hashed_password = utils.hash_password(password)

    user = datastore.create_user(
        email=email,
        password=hashed_password,
        roles=[examiner_role]
    )

    db.session.flush()

    examiner = Examiner(
        user_id=user.id,
        fullname=fullname,
        employee_id=employee_id,
        contact=contact or None,
        department=department or None,
        designation=designation or None
    )

    db.session.add(examiner)

    db.session.commit()

    return {
        'message': 'Examiner account created successfully.',

        'examiner': {
            'id': examiner.id,
            'fullname': examiner.fullname,
            'email': user.email,
            'employee_id': examiner.employee_id,
            'contact': examiner.contact,
            'department': examiner.department,
            'designation': examiner.designation,
            'status': user.status,
            'role': 'examiner'
        }
    }, 201


# --------------------------------------------------
# EDIT EXAMINER DETAILS AND PASSWORD
# --------------------------------------------------

@admin_bp.route('/examiners/<int:examiner_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def update_examiner(examiner_id):

    data = request.get_json(silent=True) or {}

    examiner = db.session.get(
        Examiner,
        examiner_id
    )

    if not examiner:
        return {
            'message': 'Examiner not found.'
        }, 404

    fullname = str(
        data.get('fullname') or ''
    ).strip()

    email = str(
        data.get('email') or ''
    ).strip().lower()

    employee_id = str(
        data.get('employee_id') or ''
    ).strip()

    contact = str(
        data.get('contact') or ''
    ).strip()

    department = str(
        data.get('department') or ''
    ).strip()

    designation = str(
        data.get('designation') or ''
    ).strip()

    password = data.get('password', '')

    if not fullname or not email or not employee_id:
        return {
            'message': (
                'Full name, email and employee ID are required.'
            )
        }, 400

    if not isinstance(password, str):
        return {
            'message': 'Password must be a valid string.'
        }, 400

    # Validate the new password only when one is provided.
    if password and len(password) < 8:
        return {
            'message': 'Password must contain at least 8 characters.'
        }, 400

    # Check whether another account already uses this email.
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if (
        existing_user
        and existing_user.id != examiner.user_id
    ):
        return {
            'message': 'This email is already in use.'
        }, 409

    # Check whether another examiner uses this employee ID.
    existing_examiner = Examiner.query.filter_by(
        employee_id=employee_id
    ).first()

    if (
        existing_examiner
        and existing_examiner.id != examiner.id
    ):
        return {
            'message': 'This employee ID is already in use.'
        }, 409

    # Update examiner details.
    examiner.fullname = fullname

    examiner.employee_id = employee_id

    examiner.user.email = email

    examiner.contact = contact or None

    examiner.department = department or None

    examiner.designation = designation or None

    # Update the password only if the admin entered a new one.
    if password:
        examiner.user.password = utils.hash_password(password)

    db.session.commit()

    return {
        'message': (
            'Examiner details and password updated successfully.'
            if password
            else 'Examiner details updated successfully.'
        )
    }, 200


# --------------------------------------------------
# ACTIVATE OR DEACTIVATE EXAMINER
# --------------------------------------------------

@admin_bp.route(
    '/examiners/<int:examiner_id>/status',
    methods=['PATCH']
)
@auth_required('token')
@roles_required('admin')
def update_examiner_status(examiner_id):

    data = request.get_json(silent=True) or {}

    status = data.get('status', '')

    if status not in ['active', 'inactive']:
        return {
            'message': 'Status must be active or inactive.'
        }, 400

    examiner = db.session.get(
        Examiner,
        examiner_id
    )

    if not examiner:
        return {
            'message': 'Examiner not found.'
        }, 404

    examiner.user.status = status

    db.session.commit()

    return {
        'message': f'Examiner {status} successfully.',

        'status': status
    }, 200
