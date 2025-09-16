from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import Lesson, Course, Progress, Resource, Quiz, db
from functools import wraps
import os

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
    
    # Update progress
    progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson_id).first()
    if not progress:
        progress = Progress(user_id=session['user_id'], lesson_id=lesson_id)
        db.session.add(progress)
    
    progress.last_accessed = db.func.now()
    db.session.commit()
    
    # Get embedded quizzes
    embedded_quizzes = Quiz.query.filter_by(lesson_id=lesson_id).all()
    
    return render_template('lessons/view.html', lesson=lesson, embedded_quizzes=embedded_quizzes)

@lessons_bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson_id).first()
    if not progress:
        progress = Progress(user_id=session['user_id'], lesson_id=lesson_id)
        db.session.add(progress)
    
    progress.completed = True
    progress.completion_date = db.func.now()
    db.session.commit()
    
    flash('Lesson marked as completed!', 'success')
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