from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, Course, Enrollment, Progress, Lesson, QuizAttempt, Certificate, db
from functools import wraps
import uuid

student_bp = Blueprint('student', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    enrollments = Enrollment.query.filter_by(user_id=session['user_id']).all()
    
    # Calculate progress for each enrollment
    for enrollment in enrollments:
        total_lessons = Lesson.query.filter_by(course_id=enrollment.course_id).count()
        completed_lessons = Progress.query.join(Lesson).filter(
            Progress.user_id == session['user_id'],
            Progress.completed == True,
            Lesson.course_id == enrollment.course_id
        ).count()
        
        if total_lessons > 0:
            enrollment.progress_percentage = (completed_lessons / total_lessons) * 100
        else:
            enrollment.progress_percentage = 0
    
    return render_template('student/dashboard.html', user=user, enrollments=enrollments)

@student_bp.route('/student/progress/<int:course_id>')
@login_required
def view_progress(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num).all()
    
    # Get progress for each lesson
    progress_data = {}
    for lesson in lessons:
        progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson.id).first()
        progress_data[lesson.id] = progress
    
    return render_template('student/progress.html', course=course, lessons=lessons, progress_data=progress_data)

@student_bp.route('/student/grades')
@login_required
def view_grades():
    attempts = QuizAttempt.query.filter_by(user_id=session['user_id']).all()
    return render_template('student/grades.html', attempts=attempts)

@student_bp.route('/student/certificate/<int:course_id>')
@login_required
def generate_certificate(course_id):
    enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=course_id).first_or_404()
    
    # Check if course is completed
    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    completed_lessons = Progress.query.join(Lesson).filter(
        Progress.user_id == session['user_id'],
        Progress.completed == True,
        Lesson.course_id == course_id
    ).count()
    
    if completed_lessons < total_lessons:
        flash('You must complete all lessons to receive a certificate.', 'warning')
        return redirect(url_for('student.view_progress', course_id=course_id))
    
    # Check if certificate already exists
    existing_cert = Certificate.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
    if not existing_cert:
        # Generate certificate
        cert_id = str(uuid.uuid4())[:8].upper()
        certificate = Certificate(
            user_id=session['user_id'],
            course_id=course_id,
            certificate_id=cert_id
        )
        db.session.add(certificate)
        
        # Mark enrollment as completed
        enrollment.completed_at = db.func.now()
        enrollment.certificate_issued = True
        
        db.session.commit()
        
        flash('Certificate generated successfully!', 'success')
    
    certificate = Certificate.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
    return render_template('student/certificate.html', certificate=certificate)