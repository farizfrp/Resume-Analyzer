#!/bin/bash

echo "🔧 Setting up environment configuration..."

if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Copy the example file
if [ -f "env.example" ]; then
    cp env.example .env
    echo "✅ Created .env file from env.example"
    echo ""
    echo "📝 Next steps:"
    echo "1. Edit the .env file with your text editor"
    echo "2. Replace 'your_openai_api_key_here' with your actual OpenAI API key"
    echo "3. Save the file"
    echo ""
    echo "💡 To get an OpenAI API key:"
    echo "   Visit: https://platform.openai.com/api-keys"
    echo ""
    echo "🚀 After adding your API key, run: ./start.sh"
else
    echo "❌ env.example file not found!"
    echo "Creating basic .env file..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "✅ Created basic .env file"
    echo ""
    echo "📝 Please edit .env and add your OpenAI API key"
fi 