from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.examiner import examiner_bp
from routes.student import student_bp

def register_routes(app):
    app.register_blueprint(auth_bp,url_prefix='/api/auth')
    app.register_blueprint(admin_bp,url_prefix='/api/admin')
    app.register_blueprint(examiner_bp,url_prefix='/api/examiner')
    app.register_blueprint(student_bp,url_prefix='/api/student')