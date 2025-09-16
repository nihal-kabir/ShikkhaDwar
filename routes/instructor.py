from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Course, Lesson, Quiz, Question, Resource, Enrollment, Announcement, QuizAttempt, db
from werkzeug.utils import secure_filename
from functools import wraps
from constants import (
    MSG_ACCESS_DENIED, MSG_INSTRUCTOR_REQUIRED, ENDPOINT_INSTRUCTOR_MANAGE_COURSE, 
    ENDPOINT_INSTRUCTOR_DASHBOARD, TEMPLATE_INSTRUCTOR_DASHBOARD, TEMPLATE_CREATE_COURSE, 
    TEMPLATE_MANAGE_COURSE
)
import os
import json

instructor_bp = Blueprint('instructor', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'instructor':
            flash(MSG_INSTRUCTOR_REQUIRED, 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@instructor_bp.route('/instructor/dashboard')
@instructor_required
def dashboard():
    user = User.query.get(session['user_id'])
    courses = Course.query.filter_by(instructor_id=session['user_id']).all()
    
    # Get enrollment statistics
    for course in courses:
        course.enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
    
    return render_template('instructor/dashboard.html', user=user, courses=courses)

@instructor_bp.route('/instructor/course/create', methods=['GET', 'POST'])
@instructor_required
def create_course():
    if request.method == 'POST':
        course = Course(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            instructor_id=session['user_id'],
            duration_weeks=int(request.form.get('duration_weeks', 12))
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=course.id))
    
    return render_template('instructor/create_course.html')

@instructor_bp.route('/instructor/course/<int:course_id>/manage')
@instructor_required
def manage_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if instructor owns this course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num).all()
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    return render_template('instructor/manage_course.html', course=course, lessons=lessons, quizzes=quizzes, enrollments=enrollments)

@instructor_bp.route('/instructor/course/<int:course_id>/lesson/create', methods=['GET', 'POST'])
@instructor_required
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    if request.method == 'POST':
        # Get next order number
        last_lesson = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num.desc()).first()
        next_order = (last_lesson.order_num + 1) if last_lesson else 1
        
        lesson = Lesson(
            title=request.form['title'],
            content=request.form['content'],
            video_url=request.form.get('video_url', ''),
            order_num=next_order,
            course_id=course_id,
            week_number=int(request.form.get('week_number', 1))
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash('Lesson created successfully!', 'success')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=course_id))
    
    return render_template('instructor/create_lesson.html', course=course)

@instructor_bp.route('/instructor/course/<int:course_id>/quiz/create', methods=['GET', 'POST'])
@instructor_required
def create_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    if request.method == 'POST':
        quiz = Quiz(
            title=request.form['title'],
            description=request.form['description'],
            course_id=course_id,
            quiz_type=request.form.get('quiz_type', 'lesson_quiz'),
            time_limit=int(request.form.get('time_limit', 60)),
            max_attempts=int(request.form.get('max_attempts', 3))
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('instructor.manage_quiz', quiz_id=quiz.id))
    
    return render_template('instructor/create_quiz.html', course=course)

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/manage')
@instructor_required
def manage_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()
    return render_template('instructor/manage_quiz.html', quiz=quiz, questions=questions)

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/question/create', methods=['GET', 'POST'])
@instructor_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    if request.method == 'POST':
        # Get next order number
        last_question = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num.desc()).first()
        next_order = (last_question.order_num + 1) if last_question else 1
        
        options = None
        if request.form['question_type'] == 'mcq':
            options = {
                'A': request.form['option_a'],
                'B': request.form['option_b'],
                'C': request.form['option_c'],
                'D': request.form['option_d']
            }
            options = json.dumps(options)
        
        question = Question(
            quiz_id=quiz_id,
            question_text=request.form['question_text'],
            question_type=request.form['question_type'],
            options=options,
            correct_answer=request.form['correct_answer'],
            points=int(request.form.get('points', 1)),
            order_num=next_order
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question added successfully!', 'success')
        return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))
    
    return render_template('instructor/create_question.html', quiz=quiz)

@instructor_bp.route('/instructor/course/<int:course_id>/announcement', methods=['GET', 'POST'])
@instructor_required
def create_announcement(course_id):
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    if request.method == 'POST':
        announcement = Announcement(
            title=request.form['title'],
            content=request.form['content'],
            course_id=course_id,
            author_id=session['user_id'],
            is_urgent=bool(request.form.get('is_urgent'))
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement created successfully!', 'success')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=course_id))
    
    return render_template('instructor/create_announcement.html', course=course)

@instructor_bp.route('/instructor/course/<int:course_id>/analytics')
@instructor_required
def course_analytics(course_id):
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    # Get enrollment statistics
    total_enrollments = Enrollment.query.filter_by(course_id=course_id).count()
    completed_enrollments = Enrollment.query.filter_by(course_id=course_id, certificate_issued=True).count()
    
    # Get quiz performance
    quiz_attempts = QuizAttempt.query.join(Quiz).filter(Quiz.course_id == course_id).all()
    
    return render_template('instructor/analytics.html', course=course, total_enrollments=total_enrollments, 
                         completed_enrollments=completed_enrollments, quiz_attempts=quiz_attempts)