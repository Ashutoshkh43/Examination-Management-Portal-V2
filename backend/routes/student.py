
from flask import Blueprint
from flask_security import auth_required, roles_required


student_bp = Blueprint('student', __name__)


@student_bp.get('/dashboard')
@auth_required('token')
@roles_required('student')
def student_dashboard():
    return {
        'role': 'student',
        'dashboard': 'Student Dashboard',
        'message': 'Welcome Student'
    }, 200