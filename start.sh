#!/bin/bash

echo "========================================"
echo "Fake News Detector - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -d "venv/lib/python*/site-packages/flask" ]; then
    echo "Installing dependencies..."
    echo "This may take 5-10 minutes on first run..."
    pip install -r requirements.txt
    echo ""
fi

echo ""
echo "========================================"
echo "Starting Fake News Detector..."
echo "========================================"
echo ""
echo "The application will open at:"
echo "http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python app.py
