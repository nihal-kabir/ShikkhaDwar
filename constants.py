"""
Constants for ShikkhaDwar LMS
Centralized location for all constants used throughout the application
"""

# Course Categories
CATEGORY_COMPUTER_SCIENCE = 'Computer Science'
CATEGORY_MATHEMATICS = 'Mathematics'
CATEGORY_PHYSICS = 'Physics'
CATEGORY_CHEMISTRY = 'Chemistry'
CATEGORY_BIOLOGY = 'Biology'
CATEGORY_ENGINEERING = 'Engineering'
CATEGORY_BUSINESS = 'Business'
CATEGORY_ARTS = 'Arts'

# User Roles
ROLE_ADMIN = 'admin'
ROLE_INSTRUCTOR = 'instructor'
ROLE_STUDENT = 'student'

# Template Names
TEMPLATE_LOGIN = 'auth/login.html'
TEMPLATE_REGISTER = 'auth/register.html'
TEMPLATE_DASHBOARD_STUDENT = 'student/dashboard.html'
TEMPLATE_DASHBOARD_INSTRUCTOR = 'instructor/dashboard.html'
TEMPLATE_COURSE_CATALOG = 'courses/catalog.html'
TEMPLATE_COURSE_DETAIL = 'courses/detail.html'
TEMPLATE_LESSON_VIEW = 'lessons/view.html'
TEMPLATE_QUIZ = 'assessments/quiz.html'
TEMPLATE_PROGRESS = 'student/progress.html'
TEMPLATE_GRADES = 'student/grades.html'
TEMPLATE_CERTIFICATE = 'student/certificate.html'
TEMPLATE_CREATE_COURSE = 'instructor/create_course.html'
TEMPLATE_MANAGE_COURSE = 'instructor/manage_course.html'

# Route Paths
ROUTE_LOGIN = '/auth/login'
ROUTE_REGISTER = '/auth/register'
ROUTE_LOGOUT = '/auth/logout'
ROUTE_DASHBOARD = '/dashboard'
ROUTE_COURSES = '/courses'
ROUTE_COURSE_DETAIL = '/courses/<int:course_id>'
ROUTE_ENROLL = '/courses/<int:course_id>/enroll'
ROUTE_LESSON_VIEW = '/lessons/<int:lesson_id>'
ROUTE_QUIZ_TAKE = '/quiz/<int:quiz_id>'
ROUTE_STUDENT_PROGRESS = '/student/progress'
ROUTE_STUDENT_GRADES = '/student/grades'
ROUTE_INSTRUCTOR_DASHBOARD = '/instructor/dashboard'
ROUTE_INSTRUCTOR_CREATE_COURSE = '/instructor/create-course'
ROUTE_INSTRUCTOR_MANAGE_COURSE = '/instructor/manage-course/<int:course_id>'

# Access Control Messages
MSG_ACCESS_DENIED = 'Access denied.'
MSG_LOGIN_REQUIRED = 'Please log in to access this page.'
MSG_INSTRUCTOR_REQUIRED = 'Instructor access required.'
MSG_STUDENT_REQUIRED = 'Student access required.'
MSG_ADMIN_REQUIRED = 'Administrator access required.'

# Default Passwords for Development (Use secure passwords in production)
DEFAULT_ADMIN_PASSWORD = 'SecureAdmin2024!'
DEFAULT_INSTRUCTOR_PASSWORD = 'SecureInstructor2024!'
DEFAULT_STUDENT_PASSWORD = 'SecureStudent2024!'

# File Upload Settings
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'}
MAX_FILE_SIZE_MB = 16

# Quiz and Assessment Settings
QUIZ_TIME_LIMIT_MINUTES = 60
PASSING_GRADE_PERCENTAGE = 70
MAX_QUIZ_ATTEMPTS = 3

# Progress Tracking
PROGRESS_NOT_STARTED = 0
PROGRESS_IN_PROGRESS = 50
PROGRESS_COMPLETED = 100

# Database Table References
TABLE_USERS = 'users.id'
TABLE_COURSES = 'courses.id'
TABLE_LESSONS = 'lessons.id'
TABLE_QUIZZES = 'quizzes.id'

# Database Cascade Options
CASCADE_ALL_DELETE_ORPHAN = 'all, delete-orphan'