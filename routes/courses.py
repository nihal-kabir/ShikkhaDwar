from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Course, User, Enrollment, Progress, db
from functools import wraps
from constants import ROLE_INSTRUCTOR

courses_bp = Blueprint('courses', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@courses_bp.route('/courses')
def course_catalog():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Course.query.filter_by(is_published=True)
    
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%') | Course.description.ilike(f'%{search}%'))
    
    if category:
        query = query.filter_by(category=category)
    
    courses = query.all()
    categories = db.session.query(Course.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('courses/catalog.html', courses=courses, categories=categories, search=search, category=category)

@courses_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = False
    progress_data = {}
    
    if 'user_id' in session:
        enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
        is_enrolled = enrollment is not None
        
        # Get progress for each lesson if enrolled
        if is_enrolled:
            for lesson in course.lessons:
                progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson.id).first()
                progress_data[lesson.id] = progress
    
    return render_template('courses/detail.html', course=course, is_enrolled=is_enrolled, progress_data=progress_data)

@courses_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Get current user
    user = User.query.get(session['user_id'])

    # Check if user is an instructor
    if user.role == ROLE_INSTRUCTOR:
        flash('Instructors cannot enroll in courses. You can audit courses by viewing them directly.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))

    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))

    # Create enrollment
    enrollment = Enrollment(user_id=session['user_id'], course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()

    flash(f'Successfully enrolled in {course.title}!', 'success')
    return redirect(url_for('courses.course_detail', course_id=course_id))

@courses_bp.route('/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Get current user
    user = User.query.get(session['user_id'])

    # Check if user is an instructor (instructors can't be enrolled anyway)
    if user.role == ROLE_INSTRUCTOR:
        flash('Instructors are not enrolled in courses.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))

    # Check if actually enrolled
    enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
    if not enrollment:
        flash('You are not enrolled in this course.', 'warning')
        return redirect(url_for('courses.course_detail', course_id=course_id))

    try:
        # Delete the enrollment and associated progress records
        # Note: Progress records will be deleted due to cascade delete in the model
        db.session.delete(enrollment)
        db.session.commit()

        flash(f'You have been unenrolled from {course.title}.', 'info')
        return redirect(url_for('courses.course_catalog'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error unenrolling from course: {str(e)}', 'error')
        return redirect(url_for('courses.course_detail', course_id=course_id))