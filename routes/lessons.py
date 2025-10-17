from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import Lesson, Course, Progress, Resource, Quiz, User, db
from functools import wraps
import os
from constants import ROLE_INSTRUCTOR

lessons_bp = Blueprint('lessons', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@lessons_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course
    user = User.query.get(session['user_id'])

    # Check if user is the instructor of this course
    is_instructor = (user.role == ROLE_INSTRUCTOR and course.instructor_id == session['user_id'])

    if is_instructor:
        # Instructor view - show editing interface
        # Get ALL quizzes (including unpublished) for this lesson
        embedded_quizzes = Quiz.query.filter_by(lesson_id=lesson_id).all()

        return render_template('lessons/instructor_view.html',
                             lesson=lesson,
                             course=course,
                             embedded_quizzes=embedded_quizzes)
    else:
        # Student view - show learning interface
        # Update progress
        progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson_id).first()
        if not progress:
            progress = Progress(user_id=session['user_id'], lesson_id=lesson_id)
            db.session.add(progress)

        progress.last_accessed = db.func.now()
        db.session.commit()

        # Get only published quizzes for students
        embedded_quizzes = Quiz.query.filter_by(lesson_id=lesson_id, is_published=True).all()

        # Get quiz attempts for the student
        from models import QuizAttempt
        quiz_attempts = {}
        for quiz in embedded_quizzes:
            attempts = QuizAttempt.query.filter_by(
                user_id=session['user_id'],
                quiz_id=quiz.id
            ).order_by(QuizAttempt.attempt_number).all()
            quiz_attempts[quiz.id] = attempts

        return render_template('lessons/view.html',
                             lesson=lesson,
                             embedded_quizzes=embedded_quizzes,
                             quiz_attempts=quiz_attempts)

@lessons_bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    # Check if user is an instructor
    user = User.query.get(session['user_id'])
    lesson = Lesson.query.get_or_404(lesson_id)

    if user.role == ROLE_INSTRUCTOR and lesson.course.instructor_id == session['user_id']:
        flash('Instructors cannot mark lessons as complete. This feature is for students only.', 'warning')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    try:
        progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson_id).first()
        if not progress:
            progress = Progress(user_id=session['user_id'], lesson_id=lesson_id)
            db.session.add(progress)

        progress.completed = True
        progress.completion_date = db.func.now()
        db.session.commit()

        # Check if request is AJAX (JSON)
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return {'success': True, 'message': 'Lesson marked as completed!'}
        else:
            flash('Lesson marked as completed!', 'success')
            return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return {'success': False, 'message': 'Error marking lesson as complete'}, 500
        else:
            flash('Error marking lesson as complete', 'error')
            return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

@lessons_bp.route('/download/<int:resource_id>')
@login_required
def download_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return send_file(resource.file_path, as_attachment=True, download_name=resource.filename)

@lessons_bp.route('/lesson/<int:lesson_id>/track_time', methods=['POST'])
@login_required
def track_time(lesson_id):
    # This endpoint would track time spent on lessons
    # For now, just return success
    return {'status': 'success'}

@lessons_bp.route('/lesson/<int:lesson_id>/edit-content', methods=['POST'])
@login_required
def edit_lesson_content(lesson_id):
    """Update lesson title and content"""
    lesson = Lesson.query.get_or_404(lesson_id)
    user = User.query.get(session['user_id'])

    # Verify user is the instructor
    if user.role != ROLE_INSTRUCTOR or lesson.course.instructor_id != session['user_id']:
        flash('You do not have permission to edit this lesson.', 'error')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    try:
        lesson.title = request.form.get('title', lesson.title)
        lesson.content = request.form.get('content', lesson.content)

        db.session.commit()
        flash('Lesson content updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating lesson content: {str(e)}', 'error')

    return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

@lessons_bp.route('/lesson/<int:lesson_id>/edit-video', methods=['POST'])
@login_required
def edit_lesson_video(lesson_id):
    """Update lesson video URL"""
    lesson = Lesson.query.get_or_404(lesson_id)
    user = User.query.get(session['user_id'])

    # Verify user is the instructor
    if user.role != ROLE_INSTRUCTOR or lesson.course.instructor_id != session['user_id']:
        flash('You do not have permission to edit this lesson.', 'error')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    try:
        video_url = request.form.get('video_url', '').strip()
        lesson.video_url = video_url if video_url else None

        db.session.commit()
        flash('Video URL updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating video URL: {str(e)}', 'error')

    return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

@lessons_bp.route('/lesson/<int:lesson_id>/add-resource', methods=['POST'])
@login_required
def add_lesson_resource(lesson_id):
    """Add a new resource to the lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    user = User.query.get(session['user_id'])

    # Verify user is the instructor
    if user.role != ROLE_INSTRUCTOR or lesson.course.instructor_id != session['user_id']:
        flash('You do not have permission to add resources to this lesson.', 'error')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    try:
        from werkzeug.utils import secure_filename
        from flask import current_app
        import datetime

        uploaded_file = request.files.get('resource_file')
        resource_title = request.form.get('resource_title', '').strip()

        if not uploaded_file or not uploaded_file.filename:
            flash('Please select a file to upload.', 'warning')
            return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

        # Get file extension
        filename = secure_filename(uploaded_file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        # Allowed extensions
        ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'rar'}

        if file_ext not in ALLOWED_EXTENSIONS:
            flash(f'File type .{file_ext} not allowed. Allowed: PDF, DOC, DOCX, PPT, PPTX, TXT, ZIP, RAR', 'warning')
            return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

        # Create resources directory
        resources_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resources')
        os.makedirs(resources_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(resources_dir, unique_filename)

        # Save file
        uploaded_file.save(file_path)

        # Create resource record
        resource = Resource(
            lesson_id=lesson_id,
            title=resource_title if resource_title else filename,
            file_type=file_ext,
            file_path=file_path,
            filename=unique_filename
        )

        db.session.add(resource)
        db.session.commit()

        flash(f'Resource "{resource.title}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding resource: {str(e)}', 'error')

    return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

@lessons_bp.route('/lesson/<int:lesson_id>/delete-resource/<int:resource_id>', methods=['POST'])
@login_required
def delete_lesson_resource(lesson_id, resource_id):
    """Delete a resource from the lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    resource = Resource.query.get_or_404(resource_id)
    user = User.query.get(session['user_id'])

    # Verify user is the instructor
    if user.role != ROLE_INSTRUCTOR or lesson.course.instructor_id != session['user_id']:
        flash('You do not have permission to delete resources from this lesson.', 'error')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    # Verify resource belongs to this lesson
    if resource.lesson_id != lesson_id:
        flash('Invalid resource for this lesson.', 'error')
        return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))

    try:
        resource_title = resource.title

        # Delete file from filesystem
        if os.path.exists(resource.file_path):
            os.remove(resource.file_path)

        # Delete from database
        db.session.delete(resource)
        db.session.commit()

        flash(f'Resource "{resource_title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting resource: {str(e)}', 'error')

    return redirect(url_for('lessons.view_lesson', lesson_id=lesson_id))