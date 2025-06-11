#!/bin/bash

echo "🚀 Starting Resume Analyzer on Port 8008..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js and try again."
    echo "You can download it from: https://nodejs.org/"
    exit 1
fi

# Build React Frontend
echo "🏗️  Building React frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Build the React app
echo "📦 Building React app for production..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend build completed!"

# Setup Backend
echo "🔧 Setting up backend..."
cd ../backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing backend dependencies..."
pip install -r requirements.txt

# Check if .env file exists and has API key
if [ ! -f "../.env" ]; then
    echo "❌ No .env file found!"
    echo "Please create a .env file in the root directory with your OPENAI_API_KEY"
    echo ""
    echo "Example .env file:"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "The application requires this to run."
    exit 1
fi

# Check if .env file contains OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY" "../.env"; then
    echo "❌ OPENAI_API_KEY not found in .env file!"
    echo "Please add your OpenAI API key to the .env file:"
    echo "OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

echo "✅ .env file found with API key"

# Start the Flask app
echo ""
echo "🌟 Starting Resume Analyzer on port 8008..."
echo "🌐 Access the application at: http://localhost:8008"
echo "📡 API endpoints available at: http://localhost:8008/api/*"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py 