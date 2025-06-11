#!/bin/bash

echo "🚀 Starting Resume Analyzer Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  No .env file found. Please create a .env file with your OPENAI_API_KEY"
    echo "Example:"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "You can still run the app and enter the API key through the web interface."
fi

# Start the Flask app
echo "🌟 Starting Flask backend on port 8008..."
python app.py 