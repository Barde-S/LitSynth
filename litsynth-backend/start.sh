#!/bin/bash

# LitSynth Startup Script
echo "=================================="
echo "   LitSynth Startup Script"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Please run this script from the litsynth-backend directory"
    echo "   cd /Users/Work/Documents/Final-Year-Project/litsynth-backend"
    exit 1
fi

# Check if .env exists
if [ ! -f "src/.env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please create src/.env with your configuration"
    exit 1
fi

# Check if PINECONE_API_KEY is set
if grep -q "REPLACE_WITH_YOUR_PINECONE_KEY" src/.env; then
    echo "⚠️  WARNING: You need to set your Pinecone API key!"
    echo ""
    echo "Steps to get Pinecone key:"
    echo "1. Go to https://www.pinecone.io/"
    echo "2. Sign up (FREE)"
    echo "3. Copy your API key"
    echo "4. Edit src/.env and replace REPLACE_WITH_YOUR_PINECONE_KEY"
    echo ""
    read -p "Press Enter after you've added your Pinecone key..."
fi

# Check Python version
echo "✓ Python version: $(python3 --version)"

# Check Redis
echo -n "✓ Checking Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo "Running!"
else
    echo "❌ Not running!"
    echo ""
    echo "Redis is required. Start it with:"
    echo "  brew services start redis"
    echo "  OR"
    echo "  docker run -d -p 6379:6379 redis:latest"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data/db
echo "✓ Database directory ready"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "✓ Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing dependencies (this may take a few minutes)..."
    pip install -r src/requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "=================================="
echo "   Starting LitSynth Server"
echo "=================================="
echo ""
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
sleep 2

# Start the server
cd src
uvicorn main:app --reload --port 8000
