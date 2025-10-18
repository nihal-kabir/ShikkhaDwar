from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from models import User, Course, Lesson, Quiz, Question, Resource, Enrollment, Announcement, QuizAttempt, db
from werkzeug.utils import secure_filename
from functools import wraps
from constants import (
    MSG_ACCESS_DENIED, MSG_INSTRUCTOR_REQUIRED, ENDPOINT_INSTRUCTOR_MANAGE_COURSE,
    ENDPOINT_INSTRUCTOR_DASHBOARD, TEMPLATE_INSTRUCTOR_DASHBOARD, TEMPLATE_CREATE_COURSE,
    TEMPLATE_MANAGE_COURSE, ALLOWED_DOCUMENT_EXTENSIONS
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
    
    # Get enrollment statistics and calculate totals
    total_lessons = 0
    total_students = 0
    for course in courses:
        course.enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        total_lessons += len(course.lessons)
        total_students += course.enrollment_count
    
    return render_template('instructor/dashboard.html', user=user, courses=courses, total_lessons=total_lessons, total_students=total_students)

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
    announcements = Announcement.query.filter_by(course_id=course_id).order_by(Announcement.created_at.desc()).all()

    return render_template('instructor/manage_course.html', course=course, lessons=lessons, quizzes=quizzes, enrollments=enrollments, announcements=announcements)

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
        db.session.flush()  # Get the lesson ID before committing

        # Handle file uploads
        uploaded_files = request.files.getlist('resources')
        if uploaded_files:
            resources_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resources')
            os.makedirs(resources_dir, exist_ok=True)

            for file in uploaded_files:
                if file and file.filename:
                    # Check if file extension is allowed
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    if file_ext in ALLOWED_DOCUMENT_EXTENSIONS:
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid name conflicts
                        import time
                        timestamp = str(int(time.time()))
                        unique_filename = f"{timestamp}_{filename}"
                        file_path = os.path.join(resources_dir, unique_filename)

                        # Save the file
                        file.save(file_path)

                        # Create resource record
                        resource = Resource(
                            title=filename,
                            filename=filename,
                            file_path=file_path,
                            file_type=file_ext,
                            lesson_id=lesson.id
                        )
                        db.session.add(resource)
                    else:
                        flash(f'File {file.filename} has an unsupported format and was skipped.', 'warning')

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

    # Get optional lesson_id from query parameter
    lesson_id = request.args.get('lesson_id', type=int)
    lesson = None
    if lesson_id:
        lesson = Lesson.query.get_or_404(lesson_id)
        # Verify lesson belongs to this course
        if lesson.course_id != course_id:
            flash('Invalid lesson for this course.', 'error')
            return redirect(url_for('instructor.manage_course', course_id=course_id))

    if request.method == 'POST':
        try:
            # Get lesson_id from form (hidden field) or query param
            form_lesson_id = request.form.get('lesson_id', type=int) or lesson_id

            quiz = Quiz(
                title=request.form['title'],
                description=request.form.get('description', ''),
                instructions=request.form.get('instructions', ''),
                course_id=course_id,
                lesson_id=form_lesson_id,  # Attach to lesson if specified
                quiz_type=request.form.get('quiz_type', 'lesson_quiz'),
                time_limit=int(request.form.get('time_limit', 60)),
                max_attempts=int(request.form.get('max_attempts', 3)),
                passing_score=int(request.form.get('passing_score', 70)),
                randomize_questions='randomize_questions' in request.form,
                show_correct_answers='show_correct_answers' in request.form,
                is_published='is_published' in request.form
            )

            db.session.add(quiz)
            db.session.commit()

            flash(f'Quiz "{quiz.title}" created successfully!', 'success')
            return redirect(url_for('instructor.manage_quiz', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}', 'error')
            return render_template('instructor/create_quiz.html', course=course, lesson=lesson)

    return render_template('instructor/create_quiz.html', course=course, lesson=lesson)

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/manage')
@instructor_required
def manage_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num).all()

    # Get all quiz attempts with student information
    attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).order_by(QuizAttempt.submitted_at.desc()).all()

    # Group attempts by student
    student_stats = {}
    for attempt in attempts:
        if attempt.user_id not in student_stats:
            user = User.query.get(attempt.user_id)
            student_stats[attempt.user_id] = {
                'user': user,
                'attempts': [],
                'attempt_count': 0,
                'best_score': 0,
                'best_percentage': 0,
                'latest_attempt': None
            }

        student_stats[attempt.user_id]['attempts'].append(attempt)
        student_stats[attempt.user_id]['attempt_count'] += 1

        # Calculate percentage
        if attempt.max_score and attempt.max_score > 0:
            percentage = (attempt.score / attempt.max_score) * 100
            if percentage > student_stats[attempt.user_id]['best_percentage']:
                student_stats[attempt.user_id]['best_score'] = attempt.score
                student_stats[attempt.user_id]['best_percentage'] = percentage

        # Track latest attempt
        if not student_stats[attempt.user_id]['latest_attempt'] or attempt.submitted_at > student_stats[attempt.user_id]['latest_attempt'].submitted_at:
            student_stats[attempt.user_id]['latest_attempt'] = attempt

    return render_template('instructor/manage_quiz.html', quiz=quiz, questions=questions, student_stats=student_stats, attempts=attempts)

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/toggle-publish', methods=['POST'])
@instructor_required
def toggle_publish_quiz(quiz_id):
    """
    Toggle the publish status of a quiz.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        # Toggle the publish status
        quiz.is_published = not quiz.is_published
        db.session.commit()

        if quiz.is_published:
            flash(f'Quiz "{quiz.title}" has been published and is now visible to students!', 'success')
        else:
            flash(f'Quiz "{quiz.title}" has been unpublished and is now hidden from students.', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating quiz status: {str(e)}', 'error')

    return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@instructor_required
def edit_quiz(quiz_id):
    """
    Edit an existing quiz
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    if request.method == 'POST':
        try:
            quiz.title = request.form['title']
            quiz.description = request.form.get('description', '')
            quiz.instructions = request.form.get('instructions', '')
            quiz.time_limit = int(request.form.get('time_limit', 60))
            quiz.max_attempts = int(request.form.get('max_attempts', 3))
            quiz.passing_score = int(request.form.get('passing_score', 70))
            quiz.randomize_questions = 'randomize_questions' in request.form
            quiz.show_correct_answers = 'show_correct_answers' in request.form
            quiz.is_published = 'is_published' in request.form

            db.session.commit()

            flash(f'Quiz "{quiz.title}" updated successfully!', 'success')
            return redirect(url_for('instructor.manage_quiz', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quiz: {str(e)}', 'error')

    return render_template('instructor/edit_quiz.html', quiz=quiz, course=course)

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/delete', methods=['POST'])
@instructor_required
def delete_quiz(quiz_id):
    """
    Delete a quiz and all its questions
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        course_id = quiz.course_id
        quiz_title = quiz.title

        # Delete quiz (questions will be cascade deleted)
        db.session.delete(quiz)
        db.session.commit()

        flash(f'Quiz "{quiz_title}" has been deleted.', 'success')
        return redirect(url_for('instructor.manage_course', course_id=course_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'error')
        return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/question/create', methods=['GET', 'POST'])
@instructor_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get(quiz.course_id)
    
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))
    
    if request.method == 'POST':
        try:
            # Get next order number
            last_question = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_num.desc()).first()
            next_order = (last_question.order_num + 1) if last_question else 1

            options = None
            correct_answer = None
            question_type = request.form.get('question_type')

            if question_type == 'mcq':
                options = {
                    'A': request.form.get('option_a', ''),
                    'B': request.form.get('option_b', ''),
                    'C': request.form.get('option_c', ''),
                    'D': request.form.get('option_d', '')
                }
                options = json.dumps(options)
                correct_answer = request.form.get('correct_answer', '')
            elif question_type == 'true_false':
                # Capitalize to match what students submit (True/False)
                tf_answer = request.form.get('true_false_answer', '')
                if tf_answer:
                    correct_answer = tf_answer.capitalize()
                else:
                    raise ValueError('True/False answer is required')
            elif question_type == 'short_answer':
                correct_answer = request.form.get('short_answer_text', '')
                if not correct_answer:
                    raise ValueError('Short answer text is required')
            else:
                # For essay types
                correct_answer = request.form.get('correct_answer', '')

            question = Question(
                quiz_id=quiz_id,
                question_text=request.form.get('question_text', ''),
                question_type=question_type,
                options=options,
                correct_answer=correct_answer,
                points=int(request.form.get('points', 1)),
                order_num=next_order
            )

            db.session.add(question)
            db.session.commit()

            flash('Question added successfully!', 'success')
            return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding question: {str(e)}', 'error')
            return render_template('instructor/create_question.html', quiz=quiz)
    
    return render_template('instructor/create_question.html', quiz=quiz)

@instructor_bp.route('/instructor/question/<int:question_id>/edit', methods=['GET', 'POST'])
@instructor_required
def edit_question(question_id):
    """
    Edit an existing question
    """
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(question.quiz_id)
    course = Course.query.get(quiz.course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    if request.method == 'POST':
        try:
            question.question_text = request.form['question_text']
            question.question_type = request.form['question_type']
            question.points = int(request.form.get('points', 1))

            # Handle different question types
            if request.form['question_type'] == 'mcq':
                options = {
                    'A': request.form['option_a'],
                    'B': request.form['option_b'],
                    'C': request.form['option_c'],
                    'D': request.form['option_d']
                }
                question.options = json.dumps(options)
                question.correct_answer = request.form['correct_answer']
            elif request.form['question_type'] == 'true_false':
                question.options = None
                question.correct_answer = request.form['true_false_answer'].capitalize()
            elif request.form['question_type'] == 'short_answer':
                question.options = None
                question.correct_answer = request.form['short_answer_text']
            else:  # essay
                question.options = None
                question.correct_answer = request.form.get('correct_answer', '')

            db.session.commit()

            flash('Question updated successfully!', 'success')
            return redirect(url_for('instructor.manage_quiz', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'error')

    return render_template('instructor/edit_question.html', question=question, quiz=quiz)

@instructor_bp.route('/instructor/question/<int:question_id>/delete', methods=['POST'])
@instructor_required
def delete_question(question_id):
    """
    Delete a question
    """
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(question.quiz_id)
    course = Course.query.get(quiz.course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        quiz_id = question.quiz_id
        db.session.delete(question)
        db.session.commit()

        flash('Question deleted successfully!', 'success')
        return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'error')
        return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))

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

@instructor_bp.route('/instructor/quiz/<int:quiz_id>/update', methods=['POST'])
@instructor_required
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = Course.query.get_or_404(quiz.course_id)

    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        # Update quiz settings from form
        quiz.randomize_questions = 'randomize_questions' in request.form
        quiz.show_correct_answers = 'show_correct_answers' in request.form
        quiz.is_published = 'is_published' in request.form

        db.session.commit()
        flash('Quiz settings updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Error updating quiz settings. Please try again.', 'error')

    return redirect(url_for('instructor.manage_quiz', quiz_id=quiz_id))

@instructor_bp.route('/instructor/course/<int:course_id>/toggle-publish', methods=['POST'])
@instructor_required
def toggle_publish_course(course_id):
    """
    Toggle the publish status of a course between published and unpublished.
    """
    course = Course.query.get_or_404(course_id)

    # Verify instructor owns the course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        # Toggle the publish status
        course.is_published = not course.is_published
        db.session.commit()

        if course.is_published:
            flash(f'Course "{course.title}" has been published and is now visible to students!', 'success')
        else:
            flash(f'Course "{course.title}" has been unpublished and is now hidden from students.', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating course status: {str(e)}', 'error')

    return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=course_id))

@instructor_bp.route('/instructor/course/<int:course_id>/clone', methods=['POST'])
@instructor_required
def clone_course(course_id):
    """
    Clone a course with all its content (lessons, quizzes, questions, resources).
    The cloned course will be unpublished and have '(Copy)' appended to the title.
    """
    original_course = Course.query.get_or_404(course_id)

    # Verify instructor owns the original course
    if original_course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        # Create new course with copied data
        new_course = Course(
            title=f"{original_course.title} (Copy)",
            description=original_course.description,
            category=original_course.category,
            instructor_id=session['user_id'],
            duration_weeks=original_course.duration_weeks,
            is_published=False  # New course starts as unpublished
        )
        db.session.add(new_course)
        db.session.flush()  # Get the new course ID

        # Clone all lessons
        lesson_mapping = {}  # Map old lesson IDs to new lesson IDs
        for original_lesson in original_course.lessons:
            new_lesson = Lesson(
                title=original_lesson.title,
                content=original_lesson.content,
                video_url=original_lesson.video_url,
                order_num=original_lesson.order_num,
                course_id=new_course.id,
                week_number=original_lesson.week_number
            )
            db.session.add(new_lesson)
            db.session.flush()  # Get the new lesson ID
            lesson_mapping[original_lesson.id] = new_lesson.id

            # Clone resources for this lesson
            for original_resource in original_lesson.resources:
                new_resource = Resource(
                    title=original_resource.title,
                    filename=original_resource.filename,
                    file_path=original_resource.file_path,
                    file_type=original_resource.file_type,
                    lesson_id=new_lesson.id
                )
                db.session.add(new_resource)

        # Clone all quizzes
        for original_quiz in original_course.quizzes:
            # Map lesson_id if the quiz is embedded in a lesson
            new_lesson_id = None
            if original_quiz.lesson_id:
                new_lesson_id = lesson_mapping.get(original_quiz.lesson_id)

            new_quiz = Quiz(
                title=original_quiz.title,
                description=original_quiz.description,
                instructions=original_quiz.instructions,
                course_id=new_course.id,
                lesson_id=new_lesson_id,
                quiz_type=original_quiz.quiz_type,
                time_limit=original_quiz.time_limit,
                max_attempts=original_quiz.max_attempts,
                passing_score=original_quiz.passing_score,
                randomize_questions=original_quiz.randomize_questions,
                show_correct_answers=original_quiz.show_correct_answers,
                is_published=False,  # Unpublish quizzes in cloned course
                due_date=original_quiz.due_date
            )
            db.session.add(new_quiz)
            db.session.flush()  # Get the new quiz ID

            # Clone all questions for this quiz
            for original_question in original_quiz.questions:
                new_question = Question(
                    quiz_id=new_quiz.id,
                    question_text=original_question.question_text,
                    question_type=original_question.question_type,
                    options=original_question.options,
                    correct_answer=original_question.correct_answer,
                    points=original_question.points,
                    order_num=original_question.order_num
                )
                db.session.add(new_question)

        # Clone announcements (optional - instructor may want fresh start)
        # Uncomment if you want to clone announcements too
        # for original_announcement in original_course.announcements:
        #     new_announcement = Announcement(
        #         title=original_announcement.title,
        #         content=original_announcement.content,
        #         course_id=new_course.id,
        #         author_id=session['user_id'],
        #         is_urgent=original_announcement.is_urgent
        #     )
        #     db.session.add(new_announcement)

        db.session.commit()

        flash(f'Course "{original_course.title}" cloned successfully! The new course is unpublished.', 'success')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=new_course.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error cloning course: {str(e)}', 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_MANAGE_COURSE, course_id=course_id))

@instructor_bp.route('/instructor/course/<int:course_id>/grades')
@instructor_required
def view_course_grades(course_id):
    """View all student grades for a course"""
    course = Course.query.get_or_404(course_id)

    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    # Get all enrollments for this course
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    # Get all quizzes for this course
    quizzes = Quiz.query.filter_by(course_id=course_id).all()

    # Build student grade data
    student_grades = []
    for enrollment in enrollments:
        student = enrollment.user
        student_data = {
            'user': student,
            'enrollment': enrollment,
            'quiz_attempts': []
        }

        # Get quiz attempts for this student
        for quiz in quizzes:
            attempts = QuizAttempt.query.filter_by(
                user_id=student.id,
                quiz_id=quiz.id
            ).order_by(QuizAttempt.attempt_number.desc()).all()

            if attempts:
                # Get best attempt
                best_attempt = max(attempts, key=lambda a: a.score if a.score else 0)
                student_data['quiz_attempts'].append({
                    'quiz': quiz,
                    'attempts': attempts,
                    'best_attempt': best_attempt
                })

        student_grades.append(student_data)

    return render_template('instructor/course_grades.html',
                         course=course,
                         quizzes=quizzes,
                         student_grades=student_grades)

@instructor_bp.route('/instructor/quiz-attempt/<int:attempt_id>/update-grade', methods=['POST'])
@instructor_required
def update_quiz_grade(attempt_id):
    """Manually update a quiz attempt grade"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    quiz = attempt.quiz
    course = quiz.course

    # Verify instructor owns this course
    if course.instructor_id != session['user_id']:
        flash(MSG_ACCESS_DENIED, 'error')
        return redirect(url_for(ENDPOINT_INSTRUCTOR_DASHBOARD))

    try:
        new_score = float(request.form.get('score', 0))
        feedback = request.form.get('feedback', '').strip()

        # Validate score
        if new_score < 0 or new_score > attempt.max_score:
            flash(f'Invalid score. Must be between 0 and {attempt.max_score}', 'warning')
            return redirect(request.referrer or url_for('instructor.view_course_grades', course_id=course.id))

        # Update the attempt score
        attempt.score = new_score
        attempt.is_graded = True

        # Check if a Grade record exists, if not create one
        from models import Grade
        grade = Grade.query.filter_by(quiz_attempt_id=attempt.id).first()

        if grade:
            # Update existing grade
            grade.points_earned = new_score
            grade.max_points = attempt.max_score
            grade.feedback = feedback
            grade.graded_by = session['user_id']
            grade.graded_at = db.func.now()
        else:
            # Create new grade record
            grade = Grade(
                user_id=attempt.user_id,
                quiz_attempt_id=attempt.id,
                points_earned=new_score,
                max_points=attempt.max_score,
                feedback=feedback,
                graded_by=session['user_id']
            )
            db.session.add(grade)

        db.session.commit()

        percentage = (new_score / attempt.max_score * 100) if attempt.max_score > 0 else 0
        flash(f'Grade updated successfully! New score: {new_score}/{attempt.max_score} ({percentage:.1f}%)', 'success')

    except ValueError:
        flash('Invalid score value. Please enter a valid number.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating grade: {str(e)}', 'error')

    return redirect(request.referrer or url_for('instructor.view_course_grades', course_id=course.id))