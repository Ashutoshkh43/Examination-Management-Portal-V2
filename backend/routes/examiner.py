
from flask import Blueprint
from flask_security import auth_required, roles_required

examiner_bp = Blueprint('examiner', __name__)

@examiner_bp.get('/dashboard')
@auth_required('token')
@roles_required('examiner')
def examiner_dashboard():

    return {
        'role': 'examiner',
        'dashboard': 'Examiner Dashboard',
        'message': 'Welcome Examiner'
    }, 200