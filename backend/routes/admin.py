from datetime import datetime, date, time
from flask import Blueprint, request, current_app
from flask_security import auth_required, roles_required, utils

from controllers.database import db

from models.models import (
    User,
    Course,
    Examination,
    Student,
    Examiner,
    ExaminerAssignment,
    ExaminationRubric,
    RubricMark,
    ExaminationSlot,
    Booking,
    Evaluation
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

    examinations = Examination.query.order_by(Examination.created_at.desc()).all()
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    activities = [
        {
            'id': f'booking-{booking.id}',
            'date': booking.booking_date.strftime('%Y-%m-%d %H:%M'),
            'activity': f'{booking.status} booking for {booking.examination.examination_name}',
            'performed_by': booking.student.fullname
        }
        for booking in bookings[:8]
    ]
    activities.extend([
        {
            'id': f'examination-{exam.id}',
            'date': exam.created_at.strftime('%Y-%m-%d %H:%M'),
            'activity': f'Created examination {exam.examination_name}',
            'performed_by': 'Administrator'
        }
        for exam in examinations[:8]
    ])
    activities.sort(key=lambda item: item['date'], reverse=True)

    return {
        'role': 'admin',

        'total_courses': Course.query.count(),

        'total_examinations': Examination.query.count(),

        'total_students': Student.query.count(),

        'total_examiners': Examiner.query.count(),

        'total_slots': ExaminationSlot.query.count(),

        'total_bookings': Booking.query.count(),

        'total_rubrics': ExaminationRubric.query.count(),

        'recent_activities': activities[:10],

        'examination_statuses': [
            {
                'status': status,
                'count': sum(exam.status == status for exam in examinations)
            }
            for status in dict.fromkeys(exam.status for exam in examinations)
        ],

        'booking_statuses': [
            {
                'status': status,
                'count': sum(booking.status == status for booking in bookings)
            }
            for status in dict.fromkeys(booking.status for booking in bookings)
        ]
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

                'assigned_examinations': sum(
                    assignment.status == 'active'
                    for assignment in examiner.assignments
                )
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
        status='pending',
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
        'message': 'Examiner account created and is pending approval.',

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
            'message': 'Approve or deactivate an examiner using active or inactive status.'
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

@admin_bp.route('/courses', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_courses():

    courses = Course.query.order_by(
        Course.id.desc()
    ).all()

    return {
        'courses': [
            {
                'id': course.id,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'description': course.description,
                'status': course.status
            }
            for course in courses
        ]
    }, 200


# --------------------------------------------------
# CREATE COURSE
# --------------------------------------------------

@admin_bp.route('/courses', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_course():

    data = request.get_json(silent=True) or {}

    course_code = str(
        data.get('course_code') or ''
    ).strip().upper()

    course_name = str(
        data.get('course_name') or ''
    ).strip()

    description = str(
        data.get('description') or ''
    ).strip()

    status = str(
        data.get('status') or 'active'
    ).strip().lower()

    if not course_code or not course_name:
        return {
            'message': 'Course code and course name are required.'
        }, 400

    if status not in ['active', 'inactive']:
        return {
            'message': 'Status must be active or inactive.'
        }, 400

    existing_course = Course.query.filter_by(
        course_code=course_code
    ).first()

    if existing_course:
        return {
            'message': 'This course code already exists.'
        }, 409

    course = Course(
        course_code=course_code,
        course_name=course_name,
        description=description or None,
        status=status
    )

    db.session.add(course)
    db.session.commit()

    return {
        'message': 'Course created successfully.',
        'course': {
            'id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'description': course.description,
            'status': course.status
        }
    }, 201


# --------------------------------------------------
# UPDATE COURSE
# --------------------------------------------------

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def update_course(course_id):

    data = request.get_json(silent=True) or {}

    course = db.session.get(
        Course,
        course_id
    )

    if not course:
        return {
            'message': 'Course not found.'
        }, 404

    course_code = str(
        data.get('course_code') or ''
    ).strip().upper()

    course_name = str(
        data.get('course_name') or ''
    ).strip()

    description = str(
        data.get('description') or ''
    ).strip()

    status = str(
        data.get('status') or ''
    ).strip().lower()

    if not course_code or not course_name:
        return {
            'message': 'Course code and course name are required.'
        }, 400

    if status not in ['active', 'inactive']:
        return {
            'message': 'Status must be active or inactive.'
        }, 400

    existing_course = Course.query.filter_by(
        course_code=course_code
    ).first()

    if (
        existing_course
        and existing_course.id != course.id
    ):
        return {
            'message': 'This course code is already in use.'
        }, 409

    course.course_code = course_code
    course.course_name = course_name
    course.description = description or None
    course.status = status

    db.session.commit()

    return {
        'message': 'Course updated successfully.',
        'course': {
            'id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'description': course.description,
            'status': course.status
        }
    }, 200


# --------------------------------------------------
# DELETE COURSE
# --------------------------------------------------

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@auth_required('token')
@roles_required('admin')
def delete_course(course_id):

    course = db.session.get(
        Course,
        course_id
    )

    if not course:
        return {
            'message': 'Course not found.'
        }, 404

    # A course cannot be deleted if examinations use it.
    existing_examination = Examination.query.filter_by(
        course_id=course.id
    ).first()

    if existing_examination:
        return {
            'message': (
                'Cannot delete this course because '
                'it has examinations associated with it.'
            )
        }, 409

    db.session.delete(course)
    db.session.commit()

    return {
        'message': 'Course deleted successfully.'
    }, 200


# --------------------------------------------------
# GET ALL STUDENTS
# --------------------------------------------------

@admin_bp.route('/students', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_students():

    students = Student.query.order_by(
        Student.id.desc()
    ).all()

    return {
        'students': [
            {
                'id': student.id,
                'fullname': student.fullname,
                'registration_number': student.registration_number,
                'email': student.user.email,
                'department': student.department,
                'semester': student.semester,
                'contact': student.contact,
                'status': student.user.status,
                'bookings': Booking.query.filter_by(
                    student_id=student.id
                ).count()
            }
            for student in students
        ]
    }, 200


# --------------------------------------------------
# UPDATE STUDENT DETAILS
# --------------------------------------------------

@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def update_student(student_id):

    data = request.get_json(silent=True) or {}

    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return {
            'message': 'Student not found.'
        }, 404

    fullname = str(
        data.get('fullname') or ''
    ).strip()

    email = str(
        data.get('email') or ''
    ).strip().lower()

    registration_number = str(
        data.get('registration_number') or ''
    ).strip()

    department = str(
        data.get('department') or ''
    ).strip()

    semester = str(
        data.get('semester') or ''
    ).strip()

    contact = str(
        data.get('contact') or ''
    ).strip()

    if not fullname or not email or not registration_number:
        return {
            'message': (
                'Student name, email and registration number '
                'are required.'
            )
        }, 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if (
        existing_user
        and existing_user.id != student.user_id
    ):
        return {
            'message': 'This email is already in use.'
        }, 409

    existing_student = Student.query.filter_by(
        registration_number=registration_number
    ).first()

    if (
        existing_student
        and existing_student.id != student.id
    ):
        return {
            'message': 'This registration number is already in use.'
        }, 409

    student.fullname = fullname
    student.registration_number = registration_number
    student.department = department or None
    student.semester = semester or None
    student.contact = contact or None
    student.user.email = email

    db.session.commit()

    return {
        'message': 'Student details updated successfully.'
    }, 200


# --------------------------------------------------
# ACTIVATE OR DEACTIVATE STUDENT
# --------------------------------------------------

@admin_bp.route(
    '/students/<int:student_id>/status',
    methods=['PATCH']
)
@auth_required('token')
@roles_required('admin')
def update_student_status(student_id):

    data = request.get_json(silent=True) or {}

    status = str(
        data.get('status') or ''
    ).strip().lower()

    if status not in ['active', 'inactive']:
        return {
            'message': 'Status must be active or inactive.'
        }, 400

    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return {
            'message': 'Student not found.'
        }, 404

    student.user.status = status

    db.session.commit()

    return {
        'message': f'Student {status} successfully.',
        'status': status
    }, 200

# --------------------------------------------------
# GET ALL EXAMINATIONS AND STATUS COUNTS
# --------------------------------------------------

@admin_bp.route('/examinations', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_examinations():

    statuses = [
        'Draft',
        'Slot Creation',
        'Booking Open',
        'Closed',
        'Completed'
    ]

    examinations = Examination.query.order_by(
        Examination.id.desc()
    ).all()

    return {
        'examinations': [
            {
                'id': exam.id,
                'course_id': exam.course_id,
                'course_code': exam.course.course_code,
                'course_name': exam.course.course_name,
                'examination_name': exam.examination_name,
                'examination_type': exam.examination_type,
                'examiner_id': next(
                    (assignment.examiner_id for assignment in exam.examiner_assignments
                     if assignment.status == 'active'),
                    None
                ),
                'examiner_name': next(
                    (assignment.examiner.fullname for assignment in exam.examiner_assignments
                     if assignment.status == 'active'),
                    None
                ),
                'duration': exam.duration,
                'maximum_marks': exam.maximum_marks,
                'slot_creation_start': exam.slot_creation_start.isoformat(),
                'slot_creation_end': exam.slot_creation_end.isoformat(),
                'slot_booking_start': exam.slot_booking_start.isoformat(),
                'slot_booking_end': exam.slot_booking_end.isoformat(),
                'status': exam.status,
                'results_published': exam.results_published
            }
            for exam in examinations
        ],
        'status_counts': {
            status: Examination.query.filter_by(
                status=status
            ).count()
            for status in statuses
        }
    }, 200


# --------------------------------------------------
# CREATE EXAMINATION
# --------------------------------------------------

@admin_bp.route('/examinations', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_examination():

    data = request.get_json(silent=True) or {}

    examination_name = str(
        data.get('examination_name') or ''
    ).strip()

    examination_type = str(
        data.get('examination_type') or ''
    ).strip()

    course_id = data.get('course_id')
    examiner_id = data.get('examiner_id')
    duration = data.get('duration')
    maximum_marks = data.get('maximum_marks')
    status = str(data.get('status') or 'Draft').strip()

    allowed_statuses = [
        'Draft',
        'Slot Creation',
        'Booking Open',
        'Closed',
        'Completed'
    ]

    required_dates = [
        data.get('slot_creation_start'),
        data.get('slot_creation_end'),
        data.get('slot_booking_start'),
        data.get('slot_booking_end')
    ]

    if (
        not examination_name
        or not examination_type
        or course_id is None
        or examiner_id is None
        or duration is None
        or maximum_marks is None
        or not all(required_dates)
    ):
        return {
            'message': 'Please fill in all required fields.'
        }, 400

    course = db.session.get(Course, course_id)

    if not course:
        return {
            'message': 'Selected course was not found.'
        }, 404

    examiner = db.session.get(Examiner, examiner_id)

    if not examiner:
        return {'message': 'Selected examiner was not found.'}, 404

    if examiner.user.status != 'active':
        return {'message': 'Select an active examiner.'}, 400

    if course.status != 'active':
        return {
            'message': 'Select an active course.'
        }, 400

    if examination_type not in [
        'Viva',
        'Practical',
        'Project Demo',
        'Assessment'
    ]:
        return {
            'message': 'Invalid examination type.'
        }, 400

    try:
        duration = int(duration)
        maximum_marks = float(maximum_marks)
        dates = [
            datetime.fromisoformat(value)
            for value in required_dates
        ]
    except (TypeError, ValueError):
        return {
            'message': 'Enter valid duration, marks, and date values.'
        }, 400

    if duration <= 0 or maximum_marks <= 0:
        return {
            'message': 'Duration and maximum marks must be positive.'
        }, 400

    if dates[0] > dates[1] or dates[2] > dates[3]:
        return {
            'message': 'Start dates must be before end dates.'
        }, 400

    if status not in allowed_statuses:
        return {'message': 'Invalid examination status.'}, 400

    examination = Examination(
        course_id=course.id,
        examination_name=examination_name,
        examination_type=examination_type,
        duration=duration,
        maximum_marks=maximum_marks,
        slot_creation_start=dates[0],
        slot_creation_end=dates[1],
        slot_booking_start=dates[2],
        slot_booking_end=dates[3],
        status=status
    )

    db.session.add(examination)
    db.session.flush()
    db.session.add(ExaminerAssignment(
        examination_id=examination.id,
        examiner_id=examiner.id,
        status='active'
    ))
    db.session.commit()

    return {
        'message': 'Examination created successfully.',
        'id': examination.id
    }, 201


# --------------------------------------------------
# UPDATE EXAMINATION
# --------------------------------------------------

@admin_bp.route('/examinations/<int:examination_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def update_examination(examination_id):

    data = request.get_json(silent=True) or {}

    examination = db.session.get(
        Examination,
        examination_id
    )

    if not examination:
        return {
            'message': 'Examination not found.'
        }, 404

    examination_name = str(
        data.get('examination_name') or ''
    ).strip()

    examination_type = str(
        data.get('examination_type') or ''
    ).strip()

    course_id = data.get('course_id')
    examiner_id = data.get('examiner_id')
    duration = data.get('duration')
    maximum_marks = data.get('maximum_marks')
    status = str(data.get('status') or '').strip()

    required_dates = [
        data.get('slot_creation_start'),
        data.get('slot_creation_end'),
        data.get('slot_booking_start'),
        data.get('slot_booking_end')
    ]

    allowed_statuses = [
        'Draft',
        'Slot Creation',
        'Booking Open',
        'Closed',
        'Completed'
    ]

    if (
        not examination_name
        or not examination_type
        or course_id is None
        or examiner_id is None
        or duration is None
        or maximum_marks is None
        or not all(required_dates)
    ):
        return {
            'message': 'Please fill in all required fields.'
        }, 400

    if status not in allowed_statuses:
        return {
            'message': 'Invalid examination status.'
        }, 400

    course = db.session.get(Course, course_id)

    if not course:
        return {
            'message': 'Selected course was not found.'
        }, 404

    examiner = db.session.get(Examiner, examiner_id)

    if not examiner:
        return {'message': 'Selected examiner was not found.'}, 404

    if examiner.user.status != 'active':
        return {'message': 'Select an active examiner.'}, 400

    if course.status != 'active':
        return {
            'message': 'Select an active course.'
        }, 400

    if examination_type not in [
        'Viva',
        'Practical',
        'Project Demo',
        'Assessment'
    ]:
        return {
            'message': 'Invalid examination type.'
        }, 400

    try:
        duration = int(duration)
        maximum_marks = float(maximum_marks)
        dates = [
            datetime.fromisoformat(value)
            for value in required_dates
        ]
    except (TypeError, ValueError):
        return {
            'message': 'Enter valid duration, marks, and date values.'
        }, 400

    if duration <= 0 or maximum_marks <= 0:
        return {
            'message': 'Duration and maximum marks must be positive.'
        }, 400

    if dates[0] > dates[1] or dates[2] > dates[3]:
        return {
            'message': 'Start dates must be before end dates.'
        }, 400

    examination.course_id = course.id
    examination.examination_name = examination_name
    examination.examination_type = examination_type
    examination.duration = duration
    examination.maximum_marks = maximum_marks
    examination.slot_creation_start = dates[0]
    examination.slot_creation_end = dates[1]
    examination.slot_booking_start = dates[2]
    examination.slot_booking_end = dates[3]
    examination.status = status

    ExaminerAssignment.query.filter_by(
        examination_id=examination.id,
        status='active'
    ).update({'status': 'inactive'})

    assignment = ExaminerAssignment.query.filter_by(
        examination_id=examination.id,
        examiner_id=examiner.id
    ).first()

    if assignment:
        assignment.status = 'active'
    else:
        db.session.add(ExaminerAssignment(
            examination_id=examination.id,
            examiner_id=examiner.id,
            status='active'
        ))

    db.session.commit()

    return {
        'message': 'Examination updated successfully.'
    }, 200


# --------------------------------------------------
# DELETE EXAMINATION
# --------------------------------------------------

@admin_bp.route(
    '/examinations/<int:examination_id>',
    methods=['DELETE']
)
@auth_required('token')
@roles_required('admin')
def delete_examination(examination_id):

    examination = db.session.get(
        Examination,
        examination_id
    )

    if not examination:
        return {
            'message': 'Examination not found.'
        }, 404

    has_slots = ExaminationSlot.query.filter_by(
        examination_id=examination.id
    ).first()

    has_bookings = Booking.query.filter_by(
        examination_id=examination.id
    ).first()

    has_rubrics = ExaminationRubric.query.filter_by(
        examination_id=examination.id
    ).first()

    has_assignments = ExaminerAssignment.query.filter_by(
        examination_id=examination.id
    ).first()

    if has_slots or has_bookings or has_rubrics or has_assignments:
        return {
            'message': (
                'This examination cannot be deleted because it has '
                'associated slots, bookings, rubrics, or assignments.'
            )
        }, 409

    db.session.delete(examination)
    db.session.commit()

    return {
        'message': 'Examination deleted successfully.'
    }, 200


# ==========================================
# ALL EXAMINATION SLOTS
# ==========================================


def has_active_bookings(slot):
    return Booking.query.filter(
        Booking.slot_id == slot.id,
        Booking.status != 'Cancelled'
    ).first() is not None


def has_examiner_slot_conflict(
    examiner_id,
    slot_date,
    start_time,
    end_time,
    exclude_slot_id=None
):
    if examiner_id is None:
        return False

    query = ExaminationSlot.query.filter(
        ExaminationSlot.examiner_id == examiner_id,
        ExaminationSlot.date == slot_date,
        ExaminationSlot.status != 'Cancelled',
        ExaminationSlot.start_time < end_time,
        ExaminationSlot.end_time > start_time
    )

    if exclude_slot_id:
        query = query.filter(
            ExaminationSlot.id != exclude_slot_id
        )

    return query.first() is not None


# ==========================================
# GET ALL EXAMINATION SLOTS
# ==========================================


@admin_bp.route('/slots', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_all_slots():

    slots = ExaminationSlot.query.order_by(
        ExaminationSlot.date.desc(),
        ExaminationSlot.start_time
    ).all()

    slot_list = []

    for slot in slots:

        examiner = slot.examiner

        if slot.status != 'Cancelled' and slot.available_seats <= 0:
            display_status = 'Full'
        else:
            display_status = slot.status

        slot_list.append({

            'id': slot.id,

            'examination_id': slot.examination_id,
            'examination_name': slot.examination.examination_name,
            'course_code': slot.examination.course.course_code,

            'examiner_id': slot.examiner_id,
            'examiner_name': (
                examiner.fullname if examiner else 'Not Assigned'
            ),

            'date': slot.date.isoformat(),

            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),

            'capacity': slot.maximum_student_capacity,
            'available_seats': slot.available_seats,

            'booked_count': Booking.query.filter(
                Booking.slot_id == slot.id,
                Booking.status != 'Cancelled'
            ).count(),

            'status': display_status,

            'meeting_link': slot.meeting_link

        })

    awaiting_examinations = Examination.query.order_by(
        Examination.id.desc()
    ).all()
    awaiting_list = []
    for examination in awaiting_examinations:
        if examination.slots:
            continue
        assignment = ExaminerAssignment.query.filter_by(
            examination_id=examination.id,
            status='active'
        ).first()
        awaiting_list.append({
            'id': examination.id,
            'examination_name': examination.examination_name,
            'course_code': examination.course.course_code,
            'status': examination.status,
            'examiner_id': assignment.examiner_id if assignment else None,
            'examiner_name': assignment.examiner.fullname if assignment else 'Not Assigned'
        })

    return {
        'slots': slot_list,
        'awaiting_examinations': awaiting_list
    }, 200


@admin_bp.route('/slots', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_admin_slot():
    data = request.get_json(silent=True) or {}
    try:
        examination_id = int(data.get('examination_id'))
        examiner_id = int(data.get('examiner_id'))
        slot_date = date.fromisoformat(str(data.get('date') or ''))
        start_time = time.fromisoformat(str(data.get('start_time') or ''))
        end_time = time.fromisoformat(str(data.get('end_time') or ''))
        capacity = int(data.get('capacity'))
    except (TypeError, ValueError):
        return {'message': 'Enter a valid examination, examiner, date, time, and capacity.'}, 400

    if capacity < 1:
        return {'message': 'Capacity must be greater than zero.'}, 400
    if start_time >= end_time:
        return {'message': 'End time must be later than start time.'}, 400

    examination = db.session.get(Examination, examination_id)
    if not examination:
        return {'message': 'Examination not found.'}, 404
    if examination.status != 'Slot Creation':
        return {'message': 'Slots can only be added while the examination is in Slot Creation status.'}, 400

    examiner = db.session.get(Examiner, examiner_id)
    if not examiner or examiner.user.status != 'active':
        return {'message': 'Select an active examiner.'}, 400
    assignment = ExaminerAssignment.query.filter_by(
        examination_id=examination.id,
        examiner_id=examiner.id,
        status='active'
    ).first()
    if not assignment:
        return {'message': 'The examiner must be actively assigned to this examination.'}, 400

    if has_examiner_slot_conflict(examiner.id, slot_date, start_time, end_time):
        return {'message': 'The examiner already has a slot during this time.'}, 409

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


# ==========================================
# GET ACTIVE EXAMINERS
# ==========================================

@admin_bp.route('/slot-examiners', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_slot_examiners():

    examination_id = request.args.get('examination_id', type=int)

    examiner_query = Examiner.query.join(
        User,
        Examiner.user_id == User.id
    ).filter(
        User.status == 'active'
    )

    if examination_id is not None:
        examination = db.session.get(Examination, examination_id)
        if not examination:
            return {'message': 'Examination not found.'}, 404
        examiner_query = examiner_query.join(
            ExaminerAssignment,
            ExaminerAssignment.examiner_id == Examiner.id
        ).filter(
            ExaminerAssignment.examination_id == examination_id,
            ExaminerAssignment.status == 'active'
        )

    examiners = examiner_query.order_by(Examiner.fullname).all()

    return {
        'examiners': [
            {
                'id': examiner.id,
                'fullname': examiner.fullname,
                'employee_id': examiner.employee_id
            }
            for examiner in examiners
        ]
    }, 200


# ==========================================
# ADMIN BOOKING MANAGEMENT
# ==========================================

@admin_bp.route('/bookings', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_all_bookings():
    bookings = Booking.query.join(
        ExaminationSlot, Booking.slot_id == ExaminationSlot.id
    ).order_by(Booking.booking_date.desc()).all()

    return {
        'bookings': [{
            'id': booking.id,
            'student_id': booking.student_id,
            'student_name': booking.student.fullname,
            'registration_number': booking.student.registration_number,
            'examination_id': booking.examination_id,
            'examination_name': booking.examination.examination_name,
            'course_code': booking.examination.course.course_code,
            'slot_id': booking.slot_id,
            'date': booking.slot.date.isoformat(),
            'start_time': booking.slot.start_time.strftime('%H:%M'),
            'end_time': booking.slot.end_time.strftime('%H:%M'),
            'examiner_id': booking.slot.examiner_id,
            'examiner_name': booking.slot.examiner.fullname if booking.slot.examiner else 'Not Assigned',
            'status': booking.status,
            'booking_date': booking.booking_date.isoformat(),
            'cancellation_reason': booking.cancellation_reason
        } for booking in bookings]
    }, 200


@admin_bp.route('/bookings/<int:booking_id>/reschedule', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def reschedule_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return {'message': 'Booking not found.'}, 404
    if booking.status != 'Booked':
        return {'message': 'Only active bookings can be rescheduled.'}, 400

    data = request.get_json(silent=True) or {}
    try:
        new_slot_id = int(data.get('slot_id'))
    except (TypeError, ValueError):
        return {'message': 'Select a valid slot.'}, 400

    new_slot = db.session.get(ExaminationSlot, new_slot_id)
    old_slot = booking.slot
    if not new_slot or new_slot.examination_id != booking.examination_id:
        return {'message': 'Choose a slot for the same examination.'}, 400
    if new_slot.id == old_slot.id:
        return {'message': 'Choose a different slot.'}, 400
    if new_slot.status == 'Cancelled' or new_slot.available_seats < 1:
        return {'message': 'The selected slot is not available.'}, 409

    old_slot.available_seats = min(
        old_slot.maximum_student_capacity, old_slot.available_seats + 1
    )
    if old_slot.status == 'Full':
        old_slot.status = 'Available'
    new_slot.available_seats -= 1
    if new_slot.available_seats <= 0:
        new_slot.status = 'Full'
    booking.slot_id = new_slot.id
    db.session.commit()
    return {'message': 'Booking rescheduled successfully.'}, 200


@admin_bp.route('/bookings/<int:booking_id>/reassign', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def reassign_booking_examiner(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return {'message': 'Booking not found.'}, 404
    if booking.status != 'Booked':
        return {'message': 'Only active bookings can be reassigned.'}, 400

    data = request.get_json(silent=True) or {}
    try:
        examiner_id = int(data.get('examiner_id'))
    except (TypeError, ValueError):
        return {'message': 'Select a valid examiner.'}, 400

    examiner = db.session.get(Examiner, examiner_id)
    if not examiner or examiner.user.status != 'active':
        return {'message': 'The selected examiner is not active.'}, 400
    assignment = ExaminerAssignment.query.filter_by(
        examination_id=booking.examination_id,
        examiner_id=examiner.id,
        status='active'
    ).first()
    if not assignment:
        return {'message': 'The examiner is not assigned to this examination.'}, 400

    slot = booking.slot
    if has_examiner_slot_conflict(
        examiner.id, slot.date, slot.start_time, slot.end_time,
        exclude_slot_id=slot.id
    ):
        return {'message': 'The examiner already has a slot during this time.'}, 409

    # Examiner assignment belongs to the slot in the current data model, so
    # this updates the examiner shown for every booking in this slot.
    slot.examiner_id = examiner.id
    db.session.commit()
    return {'message': 'Slot examiner reassigned successfully.'}, 200


@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return {'message': 'Booking not found.'}, 404
    if booking.status != 'Booked':
        return {'message': 'Only active bookings can be cancelled.'}, 400

    booking.status = 'Cancelled'
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = 'Booking cancelled by administrator.'
    slot = booking.slot
    slot.available_seats = min(
        slot.maximum_student_capacity, slot.available_seats + 1
    )
    if slot.status == 'Full' and slot.available_seats > 0:
        slot.status = 'Available'
    db.session.commit()
    return {'message': 'Booking cancelled successfully.'}, 200


# ==========================================
# ADMIN RUBRIC MANAGEMENT
# ==========================================

def serialize_rubric(rubric):
    return {
        'id': rubric.id,
        'examination_id': rubric.examination_id,
        'examination_name': rubric.examination.examination_name,
        'course_code': rubric.examination.course.course_code,
        'criterion_name': rubric.criterion_name,
        'maximum_marks': rubric.maximum_marks,
        'weightage': rubric.weightage,
        'description': rubric.description
    }


def validate_rubric_payload(data):
    try:
        examination_id = int(data.get('examination_id'))
        maximum_marks = float(data.get('maximum_marks'))
        weightage = float(data.get('weightage')) if data.get('weightage') not in (None, '') else None
    except (TypeError, ValueError):
        return None, 'Select an examination and enter valid marks and weightage.'

    criterion_name = str(data.get('criterion_name') or '').strip()
    if not criterion_name:
        return None, 'Criterion name is required.'
    if maximum_marks <= 0:
        return None, 'Maximum marks must be greater than zero.'
    if weightage is not None and not 0 <= weightage <= 100:
        return None, 'Weightage must be between 0 and 100.'
    examination = db.session.get(Examination, examination_id)
    if not examination:
        return None, 'Examination not found.'
    return {
        'examination': examination,
        'criterion_name': criterion_name,
        'maximum_marks': maximum_marks,
        'weightage': weightage,
        'description': str(data.get('description') or '').strip() or None
    }, None


@admin_bp.route('/rubrics', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_rubrics():
    rubrics = ExaminationRubric.query.join(Examination).order_by(
        Examination.examination_name, ExaminationRubric.id
    ).all()
    return {'rubrics': [serialize_rubric(rubric) for rubric in rubrics]}, 200


@admin_bp.route('/rubrics', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_rubric():
    data = request.get_json(silent=True) or {}
    values, error = validate_rubric_payload(data)
    if error:
        return {'message': error}, 400
    rubric = ExaminationRubric(
        examination_id=values['examination'].id,
        criterion_name=values['criterion_name'],
        maximum_marks=values['maximum_marks'],
        weightage=values['weightage'],
        description=values['description']
    )
    db.session.add(rubric)
    db.session.commit()
    return {'message': 'Rubric created successfully.', 'rubric': serialize_rubric(rubric)}, 201


@admin_bp.route('/rubrics/<int:rubric_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def update_rubric(rubric_id):
    rubric = db.session.get(ExaminationRubric, rubric_id)
    if not rubric:
        return {'message': 'Rubric not found.'}, 404
    data = request.get_json(silent=True) or {}
    values, error = validate_rubric_payload(data)
    if error:
        return {'message': error}, 400
    rubric.examination_id = values['examination'].id
    rubric.criterion_name = values['criterion_name']
    rubric.maximum_marks = values['maximum_marks']
    rubric.weightage = values['weightage']
    rubric.description = values['description']
    db.session.commit()
    return {'message': 'Rubric updated successfully.', 'rubric': serialize_rubric(rubric)}, 200


@admin_bp.route('/rubrics/<int:rubric_id>', methods=['DELETE'])
@auth_required('token')
@roles_required('admin')
def delete_rubric(rubric_id):
    rubric = db.session.get(ExaminationRubric, rubric_id)
    if not rubric:
        return {'message': 'Rubric not found.'}, 404
    if RubricMark.query.filter_by(rubric_id=rubric.id).first():
        return {'message': 'This rubric is already used in an evaluation and cannot be deleted.'}, 409
    db.session.delete(rubric)
    db.session.commit()
    return {'message': 'Rubric deleted successfully.'}, 200


# ==========================================
# RESULTS AND REPORTS
# ==========================================

@admin_bp.route('/results', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_results():
    bookings = Booking.query.filter(
        Booking.status != 'Cancelled'
    ).order_by(Booking.booking_date.desc()).all()

    rows = []
    for booking in bookings:
        evaluation = booking.evaluation
        criteria = []
        if evaluation:
            criteria = [{
                'criterion_name': mark.rubric.criterion_name,
                'maximum_marks': mark.rubric.maximum_marks,
                'marks_obtained': mark.marks_obtained
            } for mark in evaluation.rubric_marks]
        rows.append({
            'booking_id': booking.id,
            'student_name': booking.student.fullname,
            'registration_number': booking.student.registration_number,
            'examination_id': booking.examination_id,
            'examination_name': booking.examination.examination_name,
            'course_code': booking.examination.course.course_code,
            'maximum_marks': booking.examination.maximum_marks,
            'date': booking.slot.date.isoformat(),
            'booking_status': booking.status,
            'evaluation_status': evaluation.status if evaluation else 'Pending',
            'total_marks': evaluation.total_marks if evaluation else None,
            'remarks': evaluation.remarks if evaluation else None,
            'result_published': bool(
                booking.examination.results_published
                and evaluation
                and evaluation.status in ['Submitted', 'Evaluated']
            ),
            'criteria': criteria
        })
    return {'results': rows}, 200


@admin_bp.route('/results/publish', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def publish_results():
    publishable_evaluations = Evaluation.query.join(
        Booking, Evaluation.booking_id == Booking.id
    ).filter(
        Evaluation.status.in_(['Submitted', 'Evaluated'])
    ).all()
    examination_ids = {evaluation.booking.examination_id for evaluation in publishable_evaluations}
    if not examination_ids:
        return {'message': 'There are no submitted evaluations to publish.', 'published_count': 0}, 400

    examinations = Examination.query.filter(
        Examination.id.in_(examination_ids)
    ).all()
    now = datetime.utcnow()
    for examination in examinations:
        examination.results_published = True
        examination.published_at = now
    db.session.commit()
    return {
        'message': 'Results published successfully.',
        'published_count': len(examinations)
    }, 200


@admin_bp.route('/reports', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_admin_reports():
    examinations = Examination.query.all()
    bookings = Booking.query.all()
    slots = ExaminationSlot.query.all()
    evaluations = Evaluation.query.filter(
        Evaluation.status.in_(['Submitted', 'Evaluated'])
    ).all()

    def counts(items, key):
        values = {}
        for item in items:
            label = key(item)
            values[label] = values.get(label, 0) + 1
        return [{'label': label, 'count': count} for label, count in sorted(values.items())]

    evaluated_booking_ids = {evaluation.booking_id for evaluation in evaluations}
    performance = []
    for evaluation in evaluations:
        booking = evaluation.booking
        maximum = booking.examination.maximum_marks
        performance.append({
            'student_name': booking.student.fullname,
            'percentage': round((evaluation.total_marks or 0) / maximum * 100, 1) if maximum else 0
        })

    examiner_activity = []
    for examiner in Examiner.query.all():
        examiner_slots = [slot for slot in slots if slot.examiner_id == examiner.id]
        examiner_bookings = [booking for booking in bookings if booking.slot.examiner_id == examiner.id]
        examiner_activity.append({
            'examiner_name': examiner.fullname,
            'slots': len(examiner_slots),
            'bookings': len(examiner_bookings),
            'evaluations': sum(booking.evaluation is not None for booking in examiner_bookings)
        })
    examiner_activity.sort(key=lambda item: item['bookings'], reverse=True)

    monthly = {}
    for slot in slots:
        month = slot.date.strftime('%Y-%m')
        row = monthly.setdefault(month, {'month': month, 'slots': 0, 'bookings': 0})
        row['slots'] += 1
        row['bookings'] += sum(booking.slot_id == slot.id for booking in bookings)

    return {
        'examinations_conducted': sum(examination.status == 'Completed' for examination in examinations),
        'students_evaluated': len(evaluated_booking_ids),
        'completed_bookings': sum(booking.status == 'Completed' for booking in bookings),
        'pending_evaluations': sum(
            booking.status == 'Booked' and booking.id not in evaluated_booking_ids
            for booking in bookings
        ),
        'examinations_by_type': counts(examinations, lambda item: item.examination_type),
        'bookings_by_status': counts(bookings, lambda item: item.status),
        'student_performance': performance,
        'examiner_activity': examiner_activity,
        'monthly_summary': [monthly[key] for key in sorted(monthly)]
    }, 200


# ==========================================
# RESCHEDULE EXAMINATION SLOT
# ==========================================

@admin_bp.route(
    '/slots/<int:slot_id>/reschedule',
    methods=['PATCH']
)
@auth_required('token')
@roles_required('admin')
def reschedule_slot(slot_id):

    data = request.get_json(silent=True) or {}

    slot = db.session.get(ExaminationSlot, slot_id)

    if not slot:
        return {'message': 'Examination slot not found.'}, 404

    if slot.status == 'Cancelled':
        return {'message': 'Cancelled slots cannot be rescheduled.'}, 400

    if has_active_bookings(slot):
        return {
            'message': 'This slot has bookings. Rescheduling is not allowed.'
        }, 400

    date_value = data.get('date', '')
    start_value = data.get('start_time', '')
    end_value = data.get('end_time', '')

    try:
        new_date = date.fromisoformat(date_value)
        new_start = time.fromisoformat(start_value)
        new_end = time.fromisoformat(end_value)
    except (ValueError, TypeError):
        return {
            'message': 'Enter a valid date and time.'
        }, 400

    if new_start >= new_end:
        return {
            'message': 'End time must be later than start time.'
        }, 400

    conflict = has_examiner_slot_conflict(
        examiner_id=slot.examiner_id,
        slot_date=new_date,
        start_time=new_start,
        end_time=new_end,
        exclude_slot_id=slot.id
    )

    if conflict:
        return {
            'message': 'The examiner already has another slot during this time.'
        }, 409

    slot.date = new_date
    slot.start_time = new_start
    slot.end_time = new_end

    db.session.commit()

    return {
        'message': 'Examination slot rescheduled successfully.'
    }, 200


# ==========================================
# REASSIGN EXAMINER
# ==========================================

@admin_bp.route(
    '/slots/<int:slot_id>/reassign',
    methods=['PATCH']
)
@auth_required('token')
@roles_required('admin')
def reassign_slot(slot_id):

    data = request.get_json(silent=True) or {}

    slot = db.session.get(ExaminationSlot, slot_id)

    if not slot:
        return {'message': 'Examination slot not found.'}, 404

    if slot.status == 'Cancelled':
        return {'message': 'Cancelled slots cannot be reassigned.'}, 400

    if has_active_bookings(slot):
        return {
            'message': 'This slot has bookings. Reassignment is not allowed.'
        }, 400

    examiner_id = data.get('examiner_id')

    if not examiner_id:
        return {
            'message': 'Please select an examiner.'
        }, 400

    examiner = db.session.get(Examiner, examiner_id)

    if not examiner:
        return {'message': 'Examiner not found.'}, 404

    if examiner.user.status != 'active':
        return {'message': 'This examiner is inactive.'}, 400

    assignment = ExaminerAssignment.query.filter_by(
        examination_id=slot.examination_id,
        examiner_id=examiner.id,
        status='active'
    ).first()

    if not assignment:
        return {
            'message': 'This examiner is not assigned to the examination.'
        }, 400

    conflict = has_examiner_slot_conflict(
        examiner_id=examiner.id,
        slot_date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        exclude_slot_id=slot.id
    )

    if conflict:
        return {
            'message': 'The selected examiner already has another slot during this time.'
        }, 409

    slot.examiner_id = examiner.id

    db.session.commit()

    return {
        'message': 'Examiner reassigned successfully.'
    }, 200


# ==========================================
# CANCEL EXAMINATION SLOT
# ==========================================

@admin_bp.route(
    '/slots/<int:slot_id>/cancel',
    methods=['PATCH']
)
@auth_required('token')
@roles_required('admin')
def cancel_slot(slot_id):

    slot = db.session.get(ExaminationSlot, slot_id)

    if not slot:
        return {'message': 'Examination slot not found.'}, 404

    if slot.status == 'Cancelled':
        return {'message': 'This slot is already cancelled.'}, 400

    for booking in Booking.query.filter(
        Booking.slot_id == slot.id,
        Booking.status != 'Cancelled'
    ).all():
        booking.status = 'Cancelled'
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = 'Slot cancelled by administrator.'

    slot.status = 'Cancelled'

    db.session.commit()

    return {
        'message': 'Examination slot cancelled successfully.'
    }, 200
