#!/bin/bash

# Production startup script for SAS application
# Runs without development features for better performance on Raspberry Pi

set -e

echo "🚀 Starting SAS Application in Production Mode..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}📦 Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please run install script first.${NC}"
    exit 1
fi

# Check if requirements are installed
if ! python -c "import fastapi, uvicorn, serial" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing missing requirements...${NC}"
    pip install -r requirements.txt
fi

# Set production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export NEXTJS_BASE_URL=""  # Disable Next.js connection attempts

# Check serial port permissions
if [ -e "/dev/ttyUSB0" ] || [ -e "/dev/ttyACM0" ] || [ -e "/dev/serial0" ]; then
    echo -e "${GREEN}✅ Serial ports detected${NC}"
else
    echo -e "${YELLOW}⚠️  No serial ports detected - SAS will run in simulation mode${NC}"
fi

# Start the application in production mode
echo -e "${GREEN}🌐 Starting FastAPI server in production mode...${NC}"
echo -e "${YELLOW}📡 SAS communication will start automatically${NC}"
echo -e "${YELLOW}🌐 API will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}📖 API documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}🔌 WebSocket endpoint: ws://localhost:8000/ws/live-updates${NC}"
echo ""
echo -e "${GREEN}To stop the application, press Ctrl+C${NC}"
echo ""

# Run with production settings
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info \
    --no-access-log \
    --timeout-keep-alive 5 \
    --timeout-graceful-shutdown 10 