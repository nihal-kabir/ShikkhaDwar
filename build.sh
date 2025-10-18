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
python init_db.py

echo "Build completed successfully!"
