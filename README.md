# University Learning Management System (LMS)

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