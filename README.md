# ShikkhaDwar - Learning Management System

A modern, easy-to-use Learning Management System for creating and managing online courses.

**Live Demo**: https://shikkhadwar.onrender.com/

## Features

- **Course Management** - Create, publish, and manage online courses
- **Video Lessons** - YouTube integration and downloadable resources
- **Quizzes & Assessments** - Multiple question types with auto-grading
- **Progress Tracking** - Monitor student progress and completion
- **Certificates** - Automatic certificate generation on course completion
- **User Roles** - Students, Instructors, and Administrators

## 🚀 Deployment

Ready to deploy? We've made it easy!

**Deploy to Render + NeonDB:**
- ✅ Pre-configured for Render deployment
- ✅ Ready for NeonDB PostgreSQL
- ✅ Auto-deploy from `deploy` branch
- ✅ Environment variables ready

**Quick Deploy:**
1. See [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) for quick setup
2. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide

## Quick Start (Local Development)

### Automated Setup (Recommended)
- **Windows**: Run `run.bat`
- **Mac/Linux**: Run `./run.sh`

### Manual Installation

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

## Requirements

- Python 3.11+
- PostgreSQL
- Modern web browser

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Gunicorn
- **Database**: PostgreSQL (NeonDB for production)
- **Frontend**: Bootstrap, JavaScript
- **Deployment**: Render (Backend), NeonDB (Database)

## User Roles

**Students**: Enroll in courses, watch lessons, take quizzes, track progress

**Instructors**: Create courses, upload content, grade assessments, view analytics

**Administrators**: Manage users and access system-wide analytics

## Project Structure

```
ShikkhaDwar/
├── app.py                 # Main application entry
├── config.py             # Configuration settings
├── models.py             # Database models
├── init_db.py            # Database initialization
├── routes/               # Application routes
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── uploads/              # User uploads
├── build.sh              # Render build script
├── render.yaml           # Render deployment config
├── Procfile              # Process configuration
├── requirements.txt      # Python dependencies
└── runtime.txt           # Python version

Documentation:
├── README.md             # This file
├── DEPLOYMENT.md         # Detailed deployment guide
└── DEPLOY_CHECKLIST.md   # Quick deployment checklist
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Educational purposes. Free to use and modify.

---

**ShikkhaDwar** - Your Gateway to Learning
