# ShikkhaDwar - Learning Management System

A modern, easy-to-use Learning Management System for creating and managing online courses.

**Live Demo**: https://shikkhadwar-81r2.onrender.com/ (As it deploys from free-tier services, it may take a moment to wake up.)

## Features

- **Course Management** - Create, publish, and manage online courses
- **Video Lessons** - YouTube integration and downloadable resources
- **Quizzes & Assessments** - Multiple question types with auto-grading
- **Progress Tracking** - Monitor student progress and completion
- **Certificates** - Automatic certificate generation on course completion
- **User Roles** - Students, Instructors, and Administrators

## Quick Start

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/nihal-kabir/ShikkhaDwar.git
   cd ShikkhaDwar
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure database**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Initialize and run**
   ```bash
   python init_db.py
   python app.py
   ```

Visit `http://localhost:5000` to access the application.

### Automated Setup
- **Windows**: Run `run.bat`
- **Mac/Linux**: Run `./run.sh`

## Requirements

- Python 3.8+
- PostgreSQL
- Modern web browser

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Bootstrap, JavaScript

## User Roles

**Students**: Enroll in courses, watch lessons, take quizzes, track progress

**Instructors**: Create courses, upload content, grade assessments, view analytics

**Administrators**: Manage users and access system-wide analytics

## License

Educational purposes. Free to use and modify.

---

**ShikkhaDwar** - Your Gateway to Learning
