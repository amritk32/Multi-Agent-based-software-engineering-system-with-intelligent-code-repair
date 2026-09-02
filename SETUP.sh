#!/bin/bash

# Krishna Code AI - Complete Setup and Run Script
# This script sets up and runs both backend and frontend services

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Krishna Code AI - Multi-Agent Code Generation Platform     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "run.sh" ]; then
    echo "❌ Please run this script from the root of krishna-code-ai-stack"
    exit 1
fi

# Backend Setup
echo -e "${BLUE}Setting up Backend...${NC}"
echo ""

cd backend

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet fastapi uvicorn pydantic python-dotenv langchain-openai langchain-core langgraph
echo "✓ Python dependencies installed"

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY environment variable not found${NC}"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo "   Then run the backend with: python -m uvicorn api:app --reload --port 8000"
else
    echo "✓ OPENAI_API_KEY is set"
fi

cd ..

# Frontend Setup
echo ""
echo -e "${BLUE}Setting up Frontend...${NC}"
echo ""

cd frontend

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+"
    exit 1
fi

echo "✓ Node.js found ($(node --version))"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install --legacy-peer-deps > /dev/null 2>&1
    echo "✓ Node.js dependencies installed"
else
    echo "✓ Node modules already installed"
fi

cd ..

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}To run the application:${NC}"
echo ""
echo "1️⃣  In Terminal 1 (Backend):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   export OPENAI_API_KEY='your-key-here'"
echo "   python -m uvicorn api:app --reload --port 8000"
echo ""
echo "2️⃣  In Terminal 2 (Frontend):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3️⃣  Open your browser:"
echo "   http://localhost:5173"
echo ""
echo -e "${YELLOW}Make sure the backend is running on http://localhost:8000${NC}"
echo ""
