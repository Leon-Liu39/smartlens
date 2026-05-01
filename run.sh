#!/bin/bash
# SmartLens Local Development Runner
# Requires: Redis, Nginx, Python 3.11+
# Usage: ./run.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔮 SmartLens Local Development Server${NC}"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if Redis is running
echo "Checking Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis CLI not found. Install with: brew install redis"
    exit 1
fi

if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not running. Start it with: redis-server"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Check if Nginx is installed
echo "Checking Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx not found. Install with: brew install nginx"
    exit 1
fi
echo -e "${GREEN}✓ Nginx is installed${NC}"

echo ""
echo -e "${YELLOW}Starting SmartLens backend...${NC}"
echo "Backend will run on http://localhost:8001"
echo "Access dashboard at http://localhost"
echo ""

# Start backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
