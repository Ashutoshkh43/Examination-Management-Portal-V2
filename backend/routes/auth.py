
from flask import Blueprint, request, current_app
from flask_security import auth_required, current_user, utils

from controllers.database import db
from models.models import Student


auth_bp = Blueprint('auth', __name__)


def get_datastore():
    return current_app.extensions['security'].datastore

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get('email') or '').strip().lower()
    password = data.get('password')
    requested_role = str(data.get('role') or '').strip().lower()

    if not email or not isinstance(password, str) or not password:
        return {
            'message': 'Email and password are required.'
        }, 400

    if requested_role not in ['admin', 'examiner', 'student']:
        return {
            'message': 'Select a valid role.'
        }, 400

    datastore = get_datastore()
    user = datastore.find_user(email=email)

    if not user:
        return {
            'message': 'Invalid email or password.'
        }, 401

    if not utils.verify_password(password, user.password):
        # Upgrade accounts created before passwords were hashed on creation.
        if 'admin' not in [role.name for role in user.roles] or user.password != password:
            return {
                'message': 'Invalid email or password.'
            }, 401

        user.password = utils.hash_password(password)
        db.session.commit()

    if not user.active:
        return {
            'message': 'This account is inactive.'
        }, 403

    user_roles = [role.name for role in user.roles]

    if requested_role not in user_roles:
        return {
            'message': 'You are not authorized to log in with this role.'
        }, 403

    token = user.get_auth_token()

    return {
        'message': 'Login successful.',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': requested_role
        },
        'redirect': '/' + requested_role + '-dashboard'
    }, 200



@auth_bp.route('/register', methods=['POST'])
def register_student():
    data = request.get_json(silent=True) or {}

    fullname = str(data.get('fullname') or '').strip()
    email = str(data.get('email') or '').strip().lower()
    password = data.get('password')
    registration_number = str(data.get('registration_number') or '').strip() or None

    if not fullname or not email or not isinstance(password, str) or not password:
        return {
            'message': 'Full name, email and password are required.'
        }, 400

    if len(password) < 8:
        return {
            'message': 'Password must contain at least 8 characters.'
        }, 400

    datastore = get_datastore()

    if datastore.find_user(email=email):
        return {
            'message': 'An account with this email already exists.'
        }, 409

    if registration_number:
        existing_student = Student.query.filter_by(
            registration_number=registration_number
        ).first()

        if existing_student:
            return {
                'message': 'Registration number already exists.'
            }, 409

    student_role = datastore.find_role('student')

    if not student_role:
        return {
            'message': 'Student role is not configured.'
        }, 500

    user = datastore.create_user(
        email=email,
        password=utils.hash_password(password),
        roles=[student_role]
    )

    db.session.flush()

    student = Student(
        user_id=user.id,
        fullname=fullname,
        registration_number=registration_number,
        department=str(data.get('department') or '').strip() or None,
        semester=str(data.get('semester') or '').strip() or None,
        contact=str(data.get('contact') or '').strip() or None
    )

    db.session.add(student)
    db.session.commit()

    return {
        'message': 'Student registered successfully.',
        'student': {
            'id': student.id,
            'fullname': student.fullname,
            'email': user.email,
            'registration_number': student.registration_number,
            'department': student.department,
            'semester': student.semester,
            'role': 'student'
        }
    }, 201

@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def get_current_user():
    user_roles = [role.name for role in current_user.roles]

    return {
        'id': current_user.id,
        'email': current_user.email,
        'roles': user_roles
    }, 200


@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    return {
        'message': 'Logout successful. Remove the saved token from the client.'
    }, 200
