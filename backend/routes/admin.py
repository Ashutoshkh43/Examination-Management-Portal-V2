from datetime import datetime
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
    hashed_password =password

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
        status='Draft'
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

            'status': display_status,

            'meeting_link': slot.meeting_link

        })

    return {
        'slots': slot_list
    }, 200


# ==========================================
# GET ACTIVE EXAMINERS
# ==========================================

@admin_bp.route('/slot-examiners', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def get_slot_examiners():

    examiners = Examiner.query.join(
        User,
        Examiner.user_id == User.id
    ).filter(
        User.status == 'active'
    ).order_by(
        Examiner.fullname
    ).all()

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

    if has_active_bookings(slot):
        return {
            'message': 'This slot has bookings. Cancel or move the bookings first.'
        }, 400

    slot.status = 'Cancelled'

    db.session.commit()

    return {
        'message': 'Examination slot cancelled successfully.'
    }, 200
