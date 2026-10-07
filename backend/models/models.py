from controllers.database import db
from datetime import datetime
from flask_security import UserMixin, RoleMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=True)

    roles = db.relationship('Role', secondary='user_roles', backref='users')
    student = db.relationship('Student', backref='user', uselist=False)
    examiner = db.relationship('Examiner', backref='user', uselist=False)

    @property
    def active(self):
        return self.status == 'active'

    @active.setter
    def active(self, value):
        self.status = 'active' if value else 'inactive'


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    fullname = db.Column(db.String(200), nullable=False)
    registration_number = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(150))
    semester = db.Column(db.String(50))
    contact = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('Booking', backref='student', lazy=True)
    evaluations = db.relationship('Evaluation', backref='student', lazy=True)


class Examiner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    fullname = db.Column(db.String(200), nullable=False)
    employee_id = db.Column(db.String(50), unique=True)
    contact = db.Column(db.String(20))
    department = db.Column(db.String(150))
    designation = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = db.relationship('ExaminerAssignment', backref='examiner', lazy=True)
    slots = db.relationship('ExaminationSlot', backref='examiner', lazy=True)
    evaluations = db.relationship('Evaluation', backref='examiner', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    examinations = db.relationship('Examination', backref='course', lazy=True)


class Examination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    examination_name = db.Column(db.String(200), nullable=False)
    examination_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    maximum_marks = db.Column(db.Float, nullable=False)
    slot_creation_start = db.Column(db.DateTime, nullable=False)
    slot_creation_end = db.Column(db.DateTime, nullable=False)
    slot_booking_start = db.Column(db.DateTime, nullable=False)
    slot_booking_end = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='Draft', nullable=False)
    results_published = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    examiner_assignments = db.relationship('ExaminerAssignment', backref='examination', lazy=True)
    slots = db.relationship('ExaminationSlot', backref='examination', lazy=True)
    rubrics = db.relationship('ExaminationRubric', backref='examination', lazy=True)
    bookings = db.relationship('Booking', backref='examination', lazy=True)


class ExaminerAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('examiner.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active', nullable=False)

    __table_args__ = (
        db.UniqueConstraint('examination_id', 'examiner_id', name='unique_examiner_examination'),
    )


class ExaminationRubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'), nullable=False)
    criterion_name = db.Column(db.String(200), nullable=False)
    maximum_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    marks = db.relationship('RubricMark', backref='rubric', lazy=True)


class ExaminationSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('examiner.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    maximum_student_capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default='Available', nullable=False)
    meeting_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('Booking', backref='slot', lazy=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('examination_slot.id'), nullable=False)
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default='Booked', nullable=False)
    cancellation_reason = db.Column(db.String(500))
    cancelled_at = db.Column(db.DateTime)

    evaluation = db.relationship('Evaluation', backref='booking', uselist=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'examination_id', name='unique_student_examination_booking'),
    )


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('examiner.id'), nullable=False)
    total_marks = db.Column(db.Float)
    remarks = db.Column(db.Text)
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='Draft', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rubric_marks = db.relationship('RubricMark', backref='evaluation', lazy=True)


class RubricMark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('examination_rubric.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('evaluation_id', 'rubric_id', name='unique_evaluation_rubric'),
    )