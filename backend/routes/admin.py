from flask import Blueprint, request, current_app
from flask_security import auth_required, current_user, utils,roles_required

admin_bp=Blueprint('admin',__name__)

@admin_bp.route('/dashboard',methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_dashboard():
    return {
        'role': 'admin',
        'dashboard': 'Admin Dashboard',
        'message': 'Welcome Admin'
    }, 200