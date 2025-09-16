#!/bin/bash

# University LMS Setup and Run Script

echo "=== University LMS Setup ==="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if MySQL is running
echo "Checking MySQL connection..."
python -c "
import pymysql
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='_03nihal.k'
    )
    print('MySQL connection successful!')
    
    # Create database if it doesn't exist
    cursor = connection.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS lms_db')
    print('Database lms_db created/verified!')
    connection.close()
except Exception as e:
    print(f'MySQL connection failed: {e}')
    print('Please ensure MySQL is running and credentials are correct.')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Initialize database
echo "Initializing database..."
python init_db.py

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Sample login credentials:"
echo "Instructor: prof_smith / password123"
echo "Student: student1 / password123"
echo "Admin: admin / admin123"
echo ""
echo "Starting the application..."
echo "Open your browser and go to: http://localhost:5000"
echo ""

# Run the application
python app.py