from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import Quiz, Question, QuizAttempt, Grade, User, Course, Enrollment, db
from functools import wraps
import json
from datetime import datetime, timezone
from sqlalchemy import func

assessments_bp = Blueprint('assessments', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

@assessments_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user is enrolled in the course
    enrollment = Enrollment.query.filter_by(
        user_id=session['user_id'], 
        course_id=quiz.course_id
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to take the quiz.', 'error')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))
    
    # Check if user has attempts left
    attempts_count = QuizAttempt.query.filter_by(
        user_id=session['user_id'], 
        quiz_id=quiz_id
    ).count()
    
    if attempts_count >= quiz.max_attempts:
        flash(f'You have exceeded the maximum number of attempts ({quiz.max_attempts}) for this quiz.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Check if quiz is published and within deadline
    if not quiz.is_published:
        flash('This quiz is not yet available.', 'warning')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))
    
    if quiz.due_date and datetime.now(timezone.utc) > quiz.due_date:
        flash('The deadline for this quiz has passed.', 'warning')
        return redirect(url_for('courses.detail', course_id=quiz.course_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()
    attempts_left = quiz.max_attempts - attempts_count
    attempts_used = attempts_count
    
    # Randomize questions if enabled
    if quiz.randomize_questions:
        import random
        questions = list(questions)
        random.shuffle(questions)
    
    return render_template('assessments/quiz.html', 
                         quiz=quiz, 
                         questions=questions,
                         attempts_left=attempts_left,
                         attempts_used=attempts_used)

@assessments_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Verify user can still submit
    attempts_count = QuizAttempt.query.filter_by(
        user_id=session['user_id'], 
        quiz_id=quiz_id
    ).count()
    
    if attempts_count >= quiz.max_attempts:
        flash('You have exceeded the maximum number of attempts.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Get current attempt number
    attempt_number = attempts_count + 1
    
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=session['user_id'],
        quiz_id=quiz_id,
        attempt_number=attempt_number,
        started_at=datetime.now(timezone.utc),
        submitted_at=datetime.now(timezone.utc),
        answers=json.dumps(dict(request.form))
    )
    
    # Auto-grade objective questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_score = 0
    max_score = sum(q.points for q in questions)
    auto_gradable = True
    
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}', '').strip()
        
        if question.question_type in ['mcq', 'true_false']:
            if user_answer.lower() == question.correct_answer.lower():
                total_score += question.points
        elif question.question_type in ['short_answer', 'essay']:
            auto_gradable = False
    
    attempt.score = total_score if auto_gradable else None
    attempt.max_score = max_score
    attempt.is_graded = auto_gradable
    
    db.session.add(attempt)
    
    # Create grade record if auto-graded
    if auto_gradable:
        grade = Grade(
            user_id=session['user_id'],
            quiz_attempt_id=attempt.id,
            points_earned=total_score,
            max_points=max_score,
            graded_by=quiz.course.instructor_id,  # System grading
            graded_at=datetime.now(timezone.utc)
        )
        db.session.add(grade)
    
    db.session.commit()
    
    if auto_gradable:
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        letter_grade = get_letter_grade(percentage)
        flash(f'Quiz submitted! Score: {total_score}/{max_score} ({percentage:.1f}% - {letter_grade})', 'success')
    else:
        flash('Quiz submitted! Your responses will be reviewed and graded by the instructor.', 'info')
    
    return redirect(url_for('student.view_grades'))

@assessments_bp.route('/gradebook/<int:course_id>')
@login_required
def gradebook(course_id):
    # Only instructors can access gradebook
    user = User.query.get(session['user_id'])
    course = Course.query.get_or_404(course_id)
    
    if user.role != 'instructor' or course.instructor_id != user.id:
        flash('Access denied. You must be the instructor of this course.', 'error')
        return redirect(url_for('courses.catalog'))
    
    # Get all quizzes for this course
    quizzes = Quiz.query.filter_by(course_id=course_id).order_by(Quiz.created_at).all()
    
    # Get all attempts for quizzes in this course
    attempts = QuizAttempt.query.join(Quiz).filter(
        Quiz.course_id == course_id
    ).join(User).order_by(User.last_name, User.first_name).all()
    
    # Get all students enrolled in the course
    enrollments = Enrollment.query.filter_by(course_id=course_id).join(User).all()
    students = [enrollment.user for enrollment in enrollments]
    
    # Calculate statistics
    if attempts:
        graded_attempts = [a for a in attempts if a.is_graded and a.score is not None]
        class_average = sum(a.score / a.max_score * 100 for a in graded_attempts) / len(graded_attempts) if graded_attempts else 0
    else:
        class_average = 0
    
    pending_grades = len([a for a in attempts if not a.is_graded])
    
    return render_template('assessments/gradebook.html', 
                         quizzes=quizzes, 
                         attempts=attempts,
                         students=students,
                         course_id=course_id,
                         course=course,
                         class_average=class_average,
                         pending_grades=pending_grades,
                         get_letter_grade=get_letter_grade)

@assessments_bp.route('/api/attempts/<int:attempt_id>')
@login_required
def get_attempt(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Check if user has permission to view this attempt
    user = User.query.get(session['user_id'])
    if user.role != 'instructor' or attempt.quiz.course.instructor_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'id': attempt.id,
        'student_name': f"{attempt.user.first_name} {attempt.user.last_name}",
        'quiz_title': attempt.quiz.title,
        'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        'max_score': attempt.max_score,
        'current_score': attempt.score,
        'answers': json.loads(attempt.answers) if attempt.answers else {}
    })

@assessments_bp.route('/api/grades/update', methods=['POST'])
@login_required
def update_grade():
    user = User.query.get(session['user_id'])
    if user.role != 'instructor':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    attempt_id = request.form.get('attempt_id')
    points_earned = float(request.form.get('points_earned'))
    max_points = float(request.form.get('max_points'))
    feedback = request.form.get('feedback', '')
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Check if instructor owns this course
    if attempt.quiz.course.instructor_id != user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Update attempt
    attempt.score = points_earned
    attempt.max_score = max_points
    attempt.is_graded = True
    
    # Create or update grade record
    grade = Grade.query.filter_by(quiz_attempt_id=attempt_id).first()
    if grade:
        grade.points_earned = points_earned
        grade.max_points = max_points
        grade.feedback = feedback
        grade.graded_at = datetime.now(timezone.utc)
    else:
        grade = Grade(
            user_id=attempt.user_id,
            quiz_attempt_id=attempt_id,
            points_earned=points_earned,
            max_points=max_points,
            feedback=feedback,
            graded_by=user.id,
            graded_at=datetime.now(timezone.utc)
        )
        db.session.add(grade)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Grade updated successfully'})

@assessments_bp.route('/api/grades/bulk-update', methods=['POST'])
@login_required
def bulk_update_grades():
    user = User.query.get(session['user_id'])
    if user.role != 'instructor':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    student_ids = data.get('students', [])
    assessment_id = data.get('assessment_id')
    grade_percent = float(data.get('grade'))
    feedback = data.get('feedback', '')
    
    quiz = Quiz.query.get_or_404(assessment_id)
    if quiz.course.instructor_id != user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    updated_count = 0
    
    for student_id in student_ids:
        # Find the latest attempt for this student and quiz
        attempt = QuizAttempt.query.filter_by(
            user_id=student_id,
            quiz_id=assessment_id
        ).order_by(QuizAttempt.attempt_number.desc()).first()
        
        if attempt:
            max_points = attempt.max_score
            points_earned = (grade_percent / 100) * max_points
            
            attempt.score = points_earned
            attempt.is_graded = True
            
            # Create or update grade record
            grade = Grade.query.filter_by(quiz_attempt_id=attempt.id).first()
            if grade:
                grade.points_earned = points_earned
                grade.max_points = max_points
                grade.feedback = feedback
                grade.graded_at = datetime.now(timezone.utc)
            else:
                grade = Grade(
                    user_id=student_id,
                    quiz_attempt_id=attempt.id,
                    points_earned=points_earned,
                    max_points=max_points,
                    feedback=feedback,
                    graded_by=user.id,
                    graded_at=datetime.now(timezone.utc)
                )
                db.session.add(grade)
            
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Updated grades for {updated_count} students'
    })

@assessments_bp.route('/api/students/<int:student_id>/performance')
@login_required
def student_performance(student_id):
    user = User.query.get(session['user_id'])
    if user.role != 'instructor':
        return jsonify({'error': 'Access denied'}), 403
    
    student = User.query.get_or_404(student_id)
    
    # Get student's attempts in instructor's courses
    attempts = QuizAttempt.query.join(Quiz).join(Course).filter(
        QuizAttempt.user_id == student_id,
        Course.instructor_id == user.id
    ).all()
    
    graded_attempts = [a for a in attempts if a.is_graded and a.score is not None]
    overall_grade = sum(a.score / a.max_score * 100 for a in graded_attempts) / len(graded_attempts) if graded_attempts else 0
    
    return jsonify({
        'student': {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email
        },
        'overall_grade': round(overall_grade, 1),
        'completed_assessments': len(graded_attempts),
        'total_assessments': len(attempts),
        'last_activity': attempts[-1].submitted_at.strftime('%B %d, %Y') if attempts else 'Never',
        'attempts': [{
            'quiz_title': a.quiz.title,
            'score': a.score,
            'max_score': a.max_score,
            'percentage': (a.score / a.max_score * 100) if a.max_score > 0 else 0,
            'submitted_at': a.submitted_at.isoformat() if a.submitted_at else None
        } for a in graded_attempts]
    })

@assessments_bp.route('/api/grades/export')
@login_required
def export_grades():
    user = User.query.get(session['user_id'])
    if user.role != 'instructor':
        return jsonify({'error': 'Access denied'}), 403
    
    course_id = request.args.get('course_id')
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Generate CSV export
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Get data
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    attempts = QuizAttempt.query.join(Quiz).filter(
        Quiz.course_id == course_id
    ).join(User).all()
    
    # Write header
    header = ['Student Name', 'Email']
    for quiz in quizzes:
        header.extend([f'{quiz.title} (Score)', f'{quiz.title} (%)'])
    header.append('Overall Average')
    writer.writerow(header)
    
    # Group attempts by student
    student_data = {}
    for attempt in attempts:
        student_id = attempt.user_id
        if student_id not in student_data:
            student_data[student_id] = {
                'user': attempt.user,
                'attempts': {}
            }
        student_data[student_id]['attempts'][attempt.quiz_id] = attempt
    
    # Write data rows
    for student_id, data in student_data.items():
        row = [
            f"{data['user'].first_name} {data['user'].last_name}",
            data['user'].email
        ]
        
        total_score = 0
        total_max = 0
        graded_count = 0
        
        for quiz in quizzes:
            if quiz.id in data['attempts']:
                attempt = data['attempts'][quiz.id]
                if attempt.is_graded and attempt.score is not None:
                    score = attempt.score
                    max_score = attempt.max_score
                    percentage = (score / max_score * 100) if max_score > 0 else 0
                    
                    row.extend([f"{score}/{max_score}", f"{percentage:.1f}%"])
                    
                    total_score += score
                    total_max += max_score
                    graded_count += 1
                else:
                    row.extend(['Pending', 'Pending'])
            else:
                row.extend(['Not Attempted', 'Not Attempted'])
        
        # Calculate overall average
        if graded_count > 0 and total_max > 0:
            overall_avg = (total_score / total_max * 100)
            row.append(f"{overall_avg:.1f}%")
        else:
            row.append('N/A')
        
        writer.writerow(row)
    
    # Return CSV file
    from flask import make_response
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={course.title}_grades.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response