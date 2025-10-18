#!/bin/bash

# ShikkhaDwar - Automated Setup and Run Script
# For Unix/Linux/Mac systems

echo "==========================================="
echo "   ShikkhaDwar - LMS Setup & Run"
echo "==========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install/Update dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from template..."
        cp .env.example .env
        echo "✓ .env file created"
        echo ""
        echo "WARNING: Please edit .env file with your database credentials"
        echo "Press Enter to continue or Ctrl+C to exit and configure .env first..."
        read
    else
        echo "Warning: No .env file found. Database configuration may be missing."
        echo ""
    fi
else
    echo "✓ .env file exists"
fi
echo ""

# Check if database needs initialization
echo "Checking database..."
if python3 -c "from models import db; from app import app; app.app_context().push(); db.create_all()" 2>/dev/null; then
    echo "✓ Database initialized/verified"
else
    echo "Initializing database..."
    python3 init_db.py
    echo "✓ Database initialized"
fi
echo ""

# Start the application
echo "==========================================="
echo "   Starting ShikkhaDwar..."
echo "==========================================="
echo ""
echo "Server will start at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
