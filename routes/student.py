from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import User, Course, Enrollment, Progress, Lesson, QuizAttempt, Certificate, Announcement, Quiz, db
from functools import wraps
import uuid
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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
    announcements = Announcement.query.filter_by(course_id=course_id).order_by(Announcement.created_at.desc()).limit(5).all()
    quizzes = Quiz.query.filter_by(course_id=course_id, is_published=True).all()

    # Get progress for each lesson
    progress_data = {}
    for lesson in lessons:
        progress = Progress.query.filter_by(user_id=session['user_id'], lesson_id=lesson.id).first()
        progress_data[lesson.id] = progress

    # Get quiz attempts for the student
    quiz_attempts = {}
    for quiz in quizzes:
        attempts = QuizAttempt.query.filter_by(user_id=session['user_id'], quiz_id=quiz.id).order_by(QuizAttempt.attempt_number).all()
        quiz_attempts[quiz.id] = attempts

    return render_template('student/progress.html', course=course, lessons=lessons, progress_data=progress_data, announcements=announcements, quizzes=quizzes, quiz_attempts=quiz_attempts)

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

@student_bp.route('/student/certificate/<int:course_id>/download')
@login_required
def download_certificate(course_id):
    """
    Generate and download certificate as PDF
    """
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

    # Check if certificate already exists, if not create it
    certificate = Certificate.query.filter_by(user_id=session['user_id'], course_id=course_id).first()
    if not certificate:
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

    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()

    # Create the PDF object using ReportLab
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Set up colors
    primary_color = colors.HexColor('#667eea')
    secondary_color = colors.HexColor('#764ba2')

    # Draw decorative border
    pdf.setStrokeColor(primary_color)
    pdf.setLineWidth(3)
    pdf.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)

    # Inner border
    pdf.setStrokeColor(secondary_color)
    pdf.setLineWidth(1)
    pdf.rect(40, 40, width - 80, height - 80, stroke=1, fill=0)

    # Add decorative corner elements
    pdf.setFillColor(primary_color)
    corner_size = 20
    # Top-left corner
    pdf.circle(50, height - 50, corner_size, stroke=0, fill=1)
    # Top-right corner
    pdf.circle(width - 50, height - 50, corner_size, stroke=0, fill=1)
    # Bottom-left corner
    pdf.circle(50, 50, corner_size, stroke=0, fill=1)
    # Bottom-right corner
    pdf.circle(width - 50, 50, corner_size, stroke=0, fill=1)

    # Title
    pdf.setFont("Helvetica-Bold", 32)
    pdf.setFillColor(primary_color)
    pdf.drawCentredString(width / 2, height - 120, "Certificate of Completion")

    # Subtitle line
    pdf.setStrokeColor(secondary_color)
    pdf.setLineWidth(2)
    pdf.line(150, height - 135, width - 150, height - 135)

    # "This is to certify that" text
    pdf.setFont("Helvetica", 14)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(width / 2, height - 180, "This is to certify that")

    # Student name
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(primary_color)
    student_name = f"{certificate.user.first_name} {certificate.user.last_name}"
    pdf.drawCentredString(width / 2, height - 220, student_name)

    # "has successfully completed the course" text
    pdf.setFont("Helvetica", 14)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(width / 2, height - 260, "has successfully completed the course")

    # Course title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(secondary_color)
    # Handle long course titles by wrapping
    course_title = certificate.course.title
    if len(course_title) > 60:
        # Split into two lines if too long
        words = course_title.split()
        line1 = ""
        line2 = ""
        for word in words:
            if len(line1 + word) < 60:
                line1 += word + " "
            else:
                line2 += word + " "
        pdf.drawCentredString(width / 2, height - 300, line1.strip())
        pdf.drawCentredString(width / 2, height - 325, line2.strip())
        details_y = height - 380
    else:
        pdf.drawCentredString(width / 2, height - 300, course_title)
        details_y = height - 355

    # "offered by ShikkhaDwar" text
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(width / 2, details_y, "offered by ShikkhaDwar LMS")

    # Details section
    details_y -= 80
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.black)

    # Left column
    left_x = 100
    pdf.drawString(left_x, details_y, "Date of Completion:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left_x, details_y - 20, certificate.issued_at.strftime('%B %d, %Y'))

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left_x, details_y - 60, "Instructor:")
    pdf.setFont("Helvetica", 11)
    instructor_name = f"{certificate.course.instructor.first_name} {certificate.course.instructor.last_name}"
    pdf.drawString(left_x, details_y - 80, instructor_name)

    # Right column
    right_x = width - 250
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(right_x, details_y, "Certificate ID:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(right_x, details_y - 20, certificate.certificate_id)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(right_x, details_y - 60, "Course Duration:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(right_x, details_y - 80, f"{certificate.course.duration_weeks} weeks")

    # Signature line
    signature_y = 150
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(1)
    pdf.line(100, signature_y, 250, signature_y)
    pdf.line(width - 250, signature_y, width - 100, signature_y)

    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(175, signature_y - 20, "Instructor Signature")
    pdf.drawCentredString(width - 175, signature_y - 20, "ShikkhaDwar LMS")

    # Footer with verification info
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.grey)
    pdf.drawCentredString(width / 2, 60, f"Verify this certificate at: {certificate.certificate_id}")
    pdf.drawCentredString(width / 2, 45, f"Generated on {datetime.now().strftime('%B %d, %Y')}")

    # Save the PDF
    pdf.showPage()
    pdf.save()

    # Move buffer position to the beginning
    buffer.seek(0)

    # Create filename
    filename = f"Certificate_{certificate.user.last_name}_{certificate.course.title.replace(' ', '_')}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )