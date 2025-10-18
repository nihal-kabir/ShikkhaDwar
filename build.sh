#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==================================="
echo "ShikkhaDwar - Render Build Script"
echo "==================================="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating upload directories..."
mkdir -p uploads
mkdir -p uploads/videos
mkdir -p uploads/resources

# Initialize database
echo "Initializing database..."
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo 'YES' || echo 'NO')"

# Run database initialization
if python init_db.py; then
    echo "Database initialization successful!"
else
    echo "Warning: Database initialization had issues, but continuing..."
    echo "The application will attempt to create tables on first run."
fi

echo "Build completed successfully!"
