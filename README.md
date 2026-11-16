# Examination Management Portal (EMP) V2

A web-based examination administration system designed to reduce the
manual work involved in planning and coordinating examinations. The
portal brings administrators, examiners, and students into one
application for managing courses, examinations, examiner assignments,
examination slots, student bookings, evaluation, and result publication.

## Problem Statement

Educational institutions often coordinate examinations through
spreadsheets, email, and manual communication. This makes it difficult
to maintain a reliable view of examination schedules, examiner
availability, slot capacity, student bookings, evaluation criteria, and
published results.

The Examination Management Portal aims to centralise these activities
and provide role-based access to the people involved in the examination
process.

## User Roles

  -----------------------------------------------------------------------
  Role                                Responsibilities
  ----------------------------------- -----------------------------------
  **Admin**                           Manages courses, examinations,
                                      examiner accounts and assignments,
                                      examination slots, students, and
                                      result publication.

  **Examiner**                        Views assigned examinations and
                                      slots, checks booked students, and
                                      evaluates students using the
                                      examination rubric.

  **Student**                         Registers and logs in, views
                                      available examinations and slots,
                                      books an eligible slot, and checks
                                      published results.
  -----------------------------------------------------------------------

## Main Modules

-   **Authentication and role-based access:** Separate access for Admin,
    Examiner, and Student.
-   **Course management:** Maintain course information used by
    examinations.
-   **Examination management:** Create and maintain examinations,
    including their type, duration, maximum marks, and scheduling
    windows.
-   **Examiner management and assignment:** Admin creates examiner
    accounts and assigns examiners to examinations.
-   **Slot management:** Create and manage individual examination
    appointments, including date, time, examiner, capacity, and
    available seats.
-   **Student booking:** Students book an available slot for an
    examination, subject to the booking window and
    one-booking-per-examination rule.
-   **Evaluation:** Examiners record marks and remarks against the
    examination's evaluation criteria.
-   **Result publication:** Admin publishes results for students to
    view.

> **Important scheduling distinction:** An examination is the overall
> assessment (for example, a Machine Learning viva). A slot is a
> specific date-and-time appointment for that examination. Creating an
> examination does not itself create a slot. The examination's
> slot-creation window controls when slots can be arranged; the booking
> window controls when students can reserve them.

## Technology Stack

### Backend

-   Python
-   Flask
-   Flask-SQLAlchemy and SQLAlchemy
-   Flask-Security for authentication and role-based access
-   SQLite
-   Flask-CORS

### Frontend

-   Vue 3
-   Vite
-   Vue Router
-   Pinia
-   Bootstrap for styling

### Planned infrastructure

-   Redis for caching
-   Celery with Redis as the broker/backend for background and batch
    jobs

Redis and Celery are part of the project requirements; confirm their
configuration and integration in the current working branch before
relying on background jobs or cache functionality.


## Prerequisites

Install the following before running the application:

-   Python 3.11 or a compatible version supported by the installed
    backend dependencies.
-   Node.js 22.18+ (or Node.js 24.12+), as specified in
    `frontend/package.json`.
-   npm.
-   Git (optional, for cloning the repository).

## Getting Started

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd Examination-Management-Portal-V2
```

### 2. Set up the backend

Open a terminal in the project directory:

``` bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

``` powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

``` cmd
venv\Scripts\activate
```

**Linux / macOS / WSL:**

``` bash
source venv/bin/activate
```

Install the backend dependencies:

``` bash
pip install -r requirements.txt
```

### 3. Configure the backend

The backend loads its settings from `backend/config.py`. This file is
intentionally excluded from version control because it contains local
configuration and credentials.

If `config.py` is not present after cloning, create it with your own
development-only values:

``` python
class Config:
    SECRET_KEY = "replace-with-a-long-random-secret"
    SECURITY_PASSWORD_SALT = "replace-with-a-random-salt"
    SQLALCHEMY_DATABASE_URI = "sqlite:///examination.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"

    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "change-this-development-password"
```

Do not commit real passwords, secret keys, or production credentials.
Change the sample administrator credentials before using the application
beyond local development.

The application initialises the SQLite database and creates the
predefined roles and administrator when the backend starts, according to
the current application setup.

### 4. Start the backend

From the `backend` directory, with the virtual environment activated:

``` bash
python app.py
```

The development API is expected at:

``` text
http://127.0.0.1:5000
```

The root endpoint (`/`) returns a message indicating that the EMP API is
running.

### 5. Set up and start the frontend

Open a second terminal:

``` bash
cd frontend
npm install
npm run dev
```

Vite prints the local frontend URL in the terminal. In the current
development setup, this is normally:

``` text
http://localhost:5173
```

Keep both the Flask backend and the Vite development server running
while using the application.

## Typical Examination Workflow

1.  Admin creates or updates a course.
2.  Admin creates an examination and configures its examination details
    and slot-creation/booking windows.
3.  Admin creates examiner accounts and assigns one or more examiners to
    the examination.
4.  Examination slots are created for specific dates and times and
    associated with an examiner.
5.  Students log in and book an available slot during the booking
    window.
6.  The assigned examiner views the booked students and conducts the
    examination.
7.  The examiner records marks and remarks using the applicable
    evaluation rubric.
8.  Admin publishes the results.
9.  Students view their results after publication.

The exact permissions for creating slots should follow the implemented
workflow in the current branch. The Admin slot-management view should
provide an institution-wide view, while an Examiner view should be
limited to that examiner's assigned examinations and slots.

## Development Notes

-   The frontend communicates with the Flask API through the project's
    API service.
-   The API uses the `Authentication-Token` header for token-based
    authenticated requests.
-   The backend currently uses SQLite for local development.
-   Do not delete the SQLite database to resolve schema changes unless
    you intentionally want to discard its data. Use a suitable migration
    or a deliberate database-rebuild procedure.
-   Keep `backend/config.py`, virtual environments, database files,
    `node_modules`, and build output out of Git.

## Current Development Status

This repository is under active development. Authentication and the
basic role structure have been established, while the examination, slot,
booking, evaluation, and result workflows are being developed and
integrated. The presence of a module in the project description does not
necessarily mean every screen, API endpoint, validation rule, or
background task is complete.

Before a demonstration or deployment, verify the complete workflow with
separate Admin, Examiner, and Student accounts, and confirm that API
permissions and booking/capacity rules are enforced by the backend.

## Future Improvements

-   Complete and validate all role-specific workflows.
-   Add automated tests for API endpoints, permissions, slot capacity,
    and booking constraints.
-   Integrate Redis caching and Celery background jobs.
-   Add audit-friendly handling for cancellations, rescheduling, and
    examiner reassignment.
-   Prepare deployment configuration and user documentation.

## Security

This project is intended for local development and demonstration unless
it has been separately hardened for production. Before deployment:

-   Use strong, unique secrets and administrator credentials.
-   Configure allowed frontend origins explicitly.
-   Use HTTPS.
-   Review authentication, authorisation, input validation, and
    password-hashing settings.
-   Protect database backups and any student or examination data.
-   Do not expose development configuration or debug mode in production.
