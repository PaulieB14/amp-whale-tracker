#!/bin/bash
# Quick start script for Amp Whale Tracker

echo "🐋 Starting Amp Whale Tracker..."
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Amp server is running
echo "🔍 Checking Amp server connection..."
python3 demo.py

# Start the dashboard
echo "🚀 Starting whale tracker dashboard..."
echo "📱 Dashboard will be available at: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop"

streamlit run whale_tracker.py