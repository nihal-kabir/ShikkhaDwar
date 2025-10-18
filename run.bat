@echo off
REM ShikkhaDwar - Automated Setup and Run Script
REM For Windows systems

echo ===========================================
echo    ShikkhaDwar - LMS Setup ^& Run
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python version:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install/Update dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env file from template...
        copy .env.example .env >nul
        echo [OK] .env file created
        echo.
        echo WARNING: Please edit .env file with your database credentials
        echo Press any key to continue or Ctrl+C to exit and configure .env first...
        pause >nul
    ) else (
        echo Warning: No .env file found. Database configuration may be missing.
        echo.
    )
) else (
    echo [OK] .env file exists
)
echo.

REM Initialize database
echo Checking database...
python init_db.py
if errorlevel 1 (
    echo Warning: Database initialization encountered issues
    echo Please check your database configuration in .env
    echo.
) else (
    echo [OK] Database initialized/verified
)
echo.

REM Start the application
echo ===========================================
echo    Starting ShikkhaDwar...
echo ===========================================
echo.
echo Server will start at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error: Application failed to start
    echo Please check the error messages above
    pause
)
