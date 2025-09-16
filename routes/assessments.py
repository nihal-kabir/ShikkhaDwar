from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Quiz, Question, QuizAttempt, Grade, User, db
from functools import wraps
import json
from datetime import datetime, timezone

assessments_bp = Blueprint('assessments', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@assessments_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has attempts left
    attempts_count = QuizAttempt.query.filter_by(user_id=session['user_id'], quiz_id=quiz_id).count()
    if attempts_count >= quiz.max_attempts:
        flash('You have exceeded the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('student.dashboard'))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()
    return render_template('assessments/quiz.html', quiz=quiz, questions=questions)

@assessments_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get current attempt number
    attempt_number = QuizAttempt.query.filter_by(user_id=session['user_id'], quiz_id=quiz_id).count() + 1
    
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=session['user_id'],
        quiz_id=quiz_id,
        attempt_number=attempt_number,
        submitted_at=datetime.now(timezone.utc),
        answers=json.dumps(dict(request.form))
    )
    
    # Auto-grade MCQ and True/False questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_score = 0
    max_score = sum(q.points for q in questions)
    
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}', '')
        if question.question_type in ['mcq', 'true_false']:
            if user_answer == question.correct_answer:
                total_score += question.points
    
    attempt.score = total_score
    attempt.max_score = max_score
    attempt.is_graded = True  # Auto-graded
    
    db.session.add(attempt)
    db.session.commit()
    
    flash(f'Quiz submitted! Score: {total_score}/{max_score}', 'success')
    return redirect(url_for('student.view_grades'))

@assessments_bp.route('/gradebook/<int:course_id>')
@login_required
def gradebook(course_id):
    # Only instructors can access gradebook
    user = User.query.get(session['user_id'])
    if user.role != 'instructor':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    attempts = QuizAttempt.query.join(Quiz).filter(Quiz.course_id == course_id).all()
    
    return render_template('assessments/gradebook.html', quizzes=quizzes, attempts=attempts)