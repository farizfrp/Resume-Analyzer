#!/bin/bash

echo "🚀 Starting Resume Analyzer Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js and try again."
    echo "You can download it from: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Start the React development server
echo "🌟 Starting React frontend..."
echo "Frontend will be available at: http://localhost:3000"
echo "Backend should be running at: http://localhost:8008"
echo ""
npm start 