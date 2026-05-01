#!/bin/bash
# SmartLens Quick Setup Script
# Usage: ./setup.sh

set -e

echo "🔮 SmartLens Setup Script"
echo "=========================="
echo ""

# Check if Python 3.11+ is installed
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Copy .env if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OpenRouter API key!"
    echo "   Get a free key at https://openrouter.ai/keys"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenRouter API key"
echo "2. For Docker: run 'docker compose up --build'"
echo "3. For local dev: run 'redis-server' and './run.sh'"
echo ""
echo "Then open http://localhost in your browser."
