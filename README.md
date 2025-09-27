# ShikkhaDwar - Learning Management System

A comprehensive Learning Management System built with Flask that provides a complete platform for online education, course management, content delivery, and progress tracking.

**Live Demo**: https://shikkhadwar.onrender.com/

## Features

### Core Functionality
- **User Management**: Role-based authentication system with students, instructors, and administrators
- **Course Management**: Complete course creation, editing, and publishing workflow
- **Content Delivery**: Video lessons with YouTube integration and downloadable resources
- **Assessment System**: Multiple quiz types (MCQ, True/False, Short Answer, Essay) with automated grading
- **Progress Tracking**: Comprehensive student progress monitoring and completion certificates
- **Communication**: Announcement system for instructor-student communication

### User Roles

**Students**
- Browse and enroll in published courses
- Access video lessons and course materials
- Take quizzes and view results
- Track learning progress
- Generate completion certificates

**Instructors**
- Create and manage courses
- Upload content and resources
- Create assessments with various question types
- Grade student submissions
- View course analytics and student progress
- Manage announcements

**Administrators**
- Full system access and user management
- System-wide analytics and reporting

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript
- **Template Engine**: Jinja2
- **Authentication**: Flask sessions with Werkzeug password hashing
- **Deployment**: Gunicorn WSGI server

## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/nihal-kabir/ShikkhaDwar.git
cd ShikkhaDwar
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Unix/Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your database credentials
```

5. **Database setup**
```bash
python init_db.py
```

6. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Quick Start (Automated)
**Windows**: Run `run.bat`
**Unix/Linux/Mac**: Run `./run.sh`

## Project Structure

```
ShikkhaDwar/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── constants.py              # Application constants
├── init_db.py               # Database initialization
├── migrate_quiz_fields.py   # Database migration script
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment configuration
├── routes/                  # Route blueprints
│   ├── auth.py             # Authentication routes
│   ├── courses.py          # Course management
│   ├── lessons.py          # Lesson content delivery
│   ├── assessments.py      # Quiz and assessment handling
│   ├── student.py          # Student dashboard and features
│   └── instructor.py       # Instructor tools and analytics
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Landing page
│   ├── auth/              # Authentication pages
│   ├── courses/           # Course-related pages
│   ├── lessons/           # Lesson viewing pages
│   ├── assessments/       # Quiz and grading pages
│   ├── student/           # Student dashboard
│   └── instructor/        # Instructor dashboard
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
└── uploads/              # User uploaded files (auto-created)
```

## Database Schema

The system includes comprehensive data models:

- **Users**: Students, instructors, and administrators with role-based permissions
- **Courses**: Course information with instructor relationships and publishing status
- **Lessons**: Individual lesson content with video integration and ordering
- **Resources**: Downloadable course materials linked to lessons
- **Enrollments**: Student course registration with progress tracking
- **Quizzes**: Assessments with multiple question types and grading options
- **Questions**: Individual quiz questions with various formats
- **QuizAttempts**: Student quiz submissions with scoring
- **Progress**: Lesson completion tracking and time spent
- **Grades**: Manual grading with instructor feedback
- **Announcements**: Course communication system
- **Certificates**: Automated certificate generation upon completion

## Configuration

The application supports multiple environments through configuration classes:

- **Development**: Debug mode enabled, local database
- **Production**: Optimized for deployment with security measures
- **Testing**: In-memory database for automated testing

Key configuration options:
- Database connection settings
- File upload limits and storage
- Security keys and session management
- Application-specific constants

## Security Features

- Password hashing using Werkzeug security utilities
- Session-based authentication with secure cookie handling
- Role-based access control for different user types
- SQL injection prevention through SQLAlchemy ORM
- File upload validation and secure filename handling
- Environment-based configuration management

## API Endpoints

The application provides RESTful routes organized by functionality:

- **Authentication**: `/register`, `/login`, `/logout`
- **Course Management**: `/courses`, `/courses/<id>`, `/enroll/<course_id>`
- **Content Delivery**: `/lessons/<id>`, `/resources/<id>/download`
- **Assessments**: `/quizzes/<id>`, `/submit-quiz`, `/quiz-results`
- **Student Features**: `/student/dashboard`, `/student/progress`, `/certificates`
- **Instructor Tools**: `/instructor/dashboard`, `/create-course`, `/manage-students`

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Migrations
```bash
python migrate_quiz_fields.py
```

### Environment Variables
Required environment variables (see `.env.example`):
- `SECRET_KEY`: Flask session security key
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database connection
- `FLASK_ENV`: Application environment (development/production/testing)

## Deployment

The application is configured for deployment on platforms like Render, Heroku, or similar PaaS providers:

1. Set environment variables in your hosting platform
2. Ensure PostgreSQL database is available
3. The `Procfile` configures Gunicorn as the WSGI server
4. Static files are served directly by Flask (suitable for small to medium applications)

## Browser Support

Tested and compatible with:
- Chrome (recommended)
- Firefox
- Safari
- Microsoft Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for educational purposes. Feel free to use and modify as needed.

## Support

For technical issues:
1. Check the application logs
2. Verify database connectivity
3. Ensure all environment variables are properly set
4. Review the project documentation

---

**ShikkhaDwar** - Empowering education through technology