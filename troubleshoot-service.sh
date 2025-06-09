#!/bin/bash

# Troubleshooting script for Spark SAS2 service issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Spark SAS2 Service Troubleshooting${NC}"
echo "=================================="
echo

# Get current directory and user info
CURRENT_DIR="$(pwd)"
CURRENT_USER="$(whoami)"

echo -e "${YELLOW}Environment Information:${NC}"
echo "  Current Directory: $CURRENT_DIR"
echo "  Current User: $CURRENT_USER"
echo "  Directory Owner: $(stat -c '%U' "$CURRENT_DIR")"
echo

# Check if virtual environment exists
echo -e "${YELLOW}Virtual Environment Check:${NC}"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Virtual environment directory exists${NC}"
    
    # Check ownership
    VENV_OWNER=$(stat -c '%U' ".venv")
    echo "  Owner: $VENV_OWNER"
    
    # Check if python exists
    if [ -f ".venv/bin/python" ]; then
        echo -e "${GREEN}✓ Python executable exists${NC}"
        
        # Test python
        if .venv/bin/python -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
            echo -e "${GREEN}✓ Python works${NC}"
        else
            echo -e "${RED}❌ Python doesn't work${NC}"
        fi
    else
        echo -e "${RED}❌ Python executable missing${NC}"
    fi
    
    # Check if uvicorn exists
    if [ -f ".venv/bin/uvicorn" ]; then
        echo -e "${GREEN}✓ Uvicorn executable exists${NC}"
        
        # Check if it's executable
        if [ -x ".venv/bin/uvicorn" ]; then
            echo -e "${GREEN}✓ Uvicorn is executable${NC}"
        else
            echo -e "${RED}❌ Uvicorn is not executable${NC}"
            echo -e "${YELLOW}💡 Fix: chmod +x .venv/bin/uvicorn${NC}"
        fi
        
        # Test uvicorn
        if .venv/bin/uvicorn --version 2>/dev/null; then
            echo -e "${GREEN}✓ Uvicorn works${NC}"
        else
            echo -e "${RED}❌ Uvicorn doesn't work${NC}"
        fi
    else
        echo -e "${RED}❌ Uvicorn executable missing${NC}"
        echo -e "${YELLOW}💡 Fix: .venv/bin/pip install uvicorn${NC}"
    fi
else
    echo -e "${RED}❌ Virtual environment doesn't exist${NC}"
    echo -e "${YELLOW}💡 Fix: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
fi

echo

# Check service file
echo -e "${YELLOW}Service Configuration Check:${NC}"
SERVICE_FILE="/etc/systemd/system/spark-sas2.service"
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${GREEN}✓ Service file exists${NC}"
    
    # Extract ExecStart line
    EXEC_START=$(grep "^ExecStart=" "$SERVICE_FILE" | cut -d'=' -f2-)
    echo "  ExecStart: $EXEC_START"
    
    # Check if the executable in ExecStart exists
    EXEC_PATH=$(echo "$EXEC_START" | awk '{print $1}')
    if [ -f "$EXEC_PATH" ]; then
        echo -e "${GREEN}✓ Service executable exists${NC}"
        
        if [ -x "$EXEC_PATH" ]; then
            echo -e "${GREEN}✓ Service executable is executable${NC}"
        else
            echo -e "${RED}❌ Service executable is not executable${NC}"
        fi
    else
        echo -e "${RED}❌ Service executable doesn't exist: $EXEC_PATH${NC}"
    fi
    
    # Check service user
    SERVICE_USER=$(grep "^User=" "$SERVICE_FILE" | cut -d'=' -f2)
    echo "  Service User: $SERVICE_USER"
    
    # Check working directory
    WORK_DIR=$(grep "^WorkingDirectory=" "$SERVICE_FILE" | cut -d'=' -f2)
    echo "  Working Directory: $WORK_DIR"
    
else
    echo -e "${RED}❌ Service file doesn't exist${NC}"
    echo -e "${YELLOW}💡 Fix: ./run-spark-service.sh install${NC}"
fi

echo

# Test manual execution
echo -e "${YELLOW}Manual Execution Test:${NC}"
if [ -f ".venv/bin/uvicorn" ] && [ -f "main.py" ]; then
    echo "Testing: .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"
    
    # Test for 3 seconds
    timeout 3 .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 &
    PID=$!
    
    sleep 2
    
    if kill -0 $PID 2>/dev/null; then
        echo -e "${GREEN}✓ Manual execution works (process started)${NC}"
        kill $PID 2>/dev/null
    else
        echo -e "${RED}❌ Manual execution failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot test - missing uvicorn or main.py${NC}"
fi

echo

# Suggested fixes
echo -e "${BLUE}🔧 Suggested Fixes:${NC}"
echo "1. Fix permissions:"
echo "   sudo chown -R $CURRENT_USER:$CURRENT_USER .venv"
echo "   chmod +x .venv/bin/*"
echo
echo "2. Reinstall service:"
echo "   ./run-spark-service.sh uninstall"
echo "   ./run-spark-service.sh install"
echo
echo "3. Test manually:"
echo "   source .venv/bin/activate"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo
echo "4. Check service logs:"
echo "   ./run-spark-service.sh logs"
echo
echo "5. If all else fails, use system Python:"
echo "   sudo pip3 install uvicorn fastapi"
echo "   # Then reinstall service" 