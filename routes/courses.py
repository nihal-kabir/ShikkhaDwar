from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Course, User, Enrollment, db
from functools import wraps

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
        query = query.filter(Course.title.contains(search) | Course.description.contains(search))
    
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
    
    if 'user_id' in session:
        enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
        is_enrolled = enrollment is not None
    
    return render_template('courses/detail.html', course=course, is_enrolled=is_enrolled)

@courses_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    
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