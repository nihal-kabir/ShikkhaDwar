# ShikkhaDwar - Learning Management System

A comprehensive Learning Management System built with Flask, featuring secure authentication, course management, content delivery, assessments, and progress tracking.

## 🛡️ Security Improvements

The codebase has been enhanced with important security and code quality improvements:

### 1. **Environment-based Configuration**
- Removed hardcoded secrets from source code
- Added secure configuration management with `config.py`
- Uses environment variables for sensitive data
- Provides `.env.example` template for local development

### 2. **Database Security**
- Eliminated hardcoded database passwords
- Secure connection string management
- Environment-based database configuration

### 3. **Code Quality Enhancements**
- **Constants Management**: Centralized all string literals in `constants.py`
- **Timezone-aware Datetime**: Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)`
- **Removed Code Duplication**: Eliminated duplicate strings for better maintainability
- **Clean Imports**: Organized imports and removed unused variables

### 4. **Configuration Files**
- **`config.py`**: Manages different environments (development, production, testing)
- **`constants.py`**: Central location for all application constants
- **`.env.example`**: Template for environment variables

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values
# CRITICAL: Update these before deployment
SECRET_KEY=your-super-secret-key-here
DB_PASSWORD=your_database_password_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Initialize database with sample data
python init_db.py
```

### 4. Run Application
```bash
python app.py
```

## 🔐 Security Configuration

### Environment Variables (`.env`)
```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here-change-this-in-production
FLASK_ENV=development

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_database_password_here
DB_NAME=lms_db
```

### Production Deployment
For production deployment:
1. Set `FLASK_ENV=production`
2. Use a strong, unique `SECRET_KEY`
3. Secure your database credentials
4. Never commit `.env` to version control

## 🔑 Default Login Credentials

**Development Environment Only:**
- **Admin**: `admin` / `SecureAdmin2024!`
- **Instructor**: `prof_smith` / `SecureInstructor2024!`
- **Student**: `student1` / `SecureStudent2024!`

⚠️ **Important**: Change these credentials before deployment to production!

## University Learning Management System (LMS)

A comprehensive Learning Management System built with Flask, MySQL, and modern web technologies.

## Features

### ✅ All 20 Required Features Implemented

**R1 — Course Catalog:**
- ✅ Course listing with search functionality
- ✅ Category-based filtering
- ✅ Course landing pages with detailed information
- ✅ Enrollment system

**R2 — Content Delivery:**
- ✅ Upload and display video lessons (YouTube integration)
- ✅ Text-based lesson content with rich formatting
- ✅ Lesson progress tracking
- ✅ Embedded quizzes within lessons
- ✅ Downloadable course resources

**R3 — Assessments & Grading:**
- ✅ Create quizzes with multiple question types (MCQ, True/False, Short Answer, Essay)
- ✅ Automatic grading for MCQ and True/False questions
- ✅ Manual grading interface for instructors
- ✅ Comprehensive gradebook view
- ✅ Grade statistics and analytics

**R4 — Student Progress:**
- ✅ Personal progress dashboard
- ✅ Course completion tracking
- ✅ Certificate generation upon completion
- ✅ Week-by-week timeline view
- ✅ Notification system for deadlines

**R5 — Instructor Tools:**
- ✅ Course analytics and engagement metrics
- ✅ Student communication via announcements
- ✅ Enrollment management
- ✅ Course creation and management tools
- ✅ Content upload and organization

## Technology Stack

- **Backend:** Flask (Python)
- **Database:** MySQL with SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Template Engine:** Jinja2
- **Authentication:** Flask sessions with password hashing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Git (optional)

### Quick Start

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd project-2
   ```

2. **Run the setup script**

   **For Windows:**
   ```bash
   run.bat
   ```
   
   **For Unix/Linux/Mac:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **Access the application**
   - Open your browser and go to: http://localhost:5000

### Manual Setup (Alternative)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   source venv/bin/activate      # Unix/Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MySQL**
   - Ensure MySQL is running
   - Update credentials in `app.py` if needed:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:_03nihal.k@localhost/lms_db'
     ```

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Default Login Credentials

**Instructor Account:**
- Username: `prof_smith`
- Password: `password123`

**Student Account:**
- Username: `student1`
- Password: `password123`

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## Project Structure

```
project-2/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── init_db.py            # Database initialization
├── requirements.txt       # Python dependencies
├── run.bat / run.sh      # Setup scripts
├── routes/               # Route blueprints
│   ├── auth.py          # Authentication routes
│   ├── courses.py       # Course management
│   ├── lessons.py       # Lesson viewing
│   ├── assessments.py   # Quiz and grading
│   ├── student.py       # Student features
│   └── instructor.py    # Instructor tools
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── auth/            # Authentication pages
│   ├── courses/         # Course pages
│   ├── lessons/         # Lesson pages
│   ├── assessments/     # Quiz pages
│   ├── student/         # Student dashboard
│   └── instructor/      # Instructor dashboard
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom CSS
│   └── js/
│       └── main.js      # Custom JavaScript
└── uploads/             # File uploads (created automatically)
```

## Key Features Detailed

### For Students:
- Browse and search course catalog
- Enroll in courses
- Watch video lessons and read content
- Download course resources
- Take quizzes and assignments
- Track progress and completion
- Generate completion certificates
- View grades and feedback

### For Instructors:
- Create and manage courses
- Upload video content and materials
- Create quizzes with various question types
- Grade student submissions
- View course analytics
- Manage student enrollments
- Send announcements to students
- Track student progress

### For Administrators:
- Manage all users and courses
- System-wide analytics
- User role management

## Database Schema

The system includes the following main entities:
- **Users** (students, instructors, admins)
- **Courses** with lessons and quizzes
- **Enrollments** tracking student course participation
- **Progress** tracking lesson completion
- **Quizzes** with questions and attempts
- **Grades** and feedback
- **Announcements** for course communication
- **Certificates** for course completion

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- SQL injection prevention with SQLAlchemy
- File upload validation
- CSRF protection ready (can be enhanced)

## Responsive Design

The application features a fully responsive design that works on:
- Desktop computers
- Tablets
- Mobile phones

## Browser Compatibility

Tested and compatible with:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

### Common Issues:

1. **MySQL Connection Error**
   - Ensure MySQL server is running
   - Verify credentials in `app.py`
   - Check if database `lms_db` exists

2. **Module Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

4. **File Upload Issues**
   - Check if `uploads/` directory exists and is writable
   - Verify file size limits in `app.py`

## Future Enhancements

- Real-time chat/messaging
- Advanced analytics dashboard
- Mobile app development
- Integration with external LTI tools
- Advanced quiz question types
- Plagiarism detection
- Video conferencing integration
- Bulk user import/export

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the error logs in the console
3. Ensure all dependencies are properly installed

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**University LMS** - A comprehensive solution for online education and course management.