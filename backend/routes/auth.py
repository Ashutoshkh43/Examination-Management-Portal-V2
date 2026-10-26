
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

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    requested_role = data.get('role', '').strip().lower()

    if not email or not password:
        return {
            'message': 'Email and password are required.'
        }, 400

    if requested_role not in ['admin', 'examiner', 'student']:
        return {
            'message': 'Select a valid role.'
        }, 400

    datastore = get_datastore()
    user = datastore.find_user(email=email)

    if not user or not utils.verify_password(password, user.password):
        return {
            'message': 'Invalid email or password.'
        }, 401

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

    fullname = data.get('fullname', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    registration_number = data.get('registration_number')

    if not fullname or not email or not password:
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
        password=password,
        roles=[student_role]
    )

    db.session.flush()

    student = Student(
        user_id=user.id,
        fullname=fullname,
        registration_number=registration_number,
        department=data.get('department'),
        semester=data.get('semester'),
        contact=data.get('contact')
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