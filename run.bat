@echo off
REM University LMS Setup and Run Script for Windows

echo === University LMS Setup ===

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Check MySQL connection and create database
echo Checking MySQL connection...
python -c "import pymysql; connection = pymysql.connect(host='localhost', user='root', password='_03nihal.k'); cursor = connection.cursor(); cursor.execute('CREATE DATABASE IF NOT EXISTS lms_db'); print('Database setup successful!'); connection.close()"

if errorlevel 1 (
    echo MySQL connection failed. Please ensure MySQL is running and credentials are correct.
    pause
    exit /b 1
)

REM Initialize database
echo Initializing database...
python init_db.py

echo.
echo === Setup Complete! ===
echo.
echo Sample login credentials:
echo Instructor: prof_smith / password123
echo Student: student1 / password123
echo Admin: admin / admin123
echo.
echo Starting the application...
echo Open your browser and go to: http://localhost:5000
echo.

REM Run the application
python app.py

pause