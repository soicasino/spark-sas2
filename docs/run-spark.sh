#!/bin/bash

# Raspberry Pi Application Runner Script
# This script activates the virtual environment and runs the Python application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Raspberry Pi Application...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment (.venv) not found!${NC}"
    echo -e "${YELLOW}Please create a virtual environment first:${NC}"
    echo "python3 -m venv .venv"
    exit 1
fi

# Check if Python application exists
if [ ! -f "rasberry-spark-soi.py" ]; then
    echo -e "${RED}Error: rasberry-spark-soi.py not found!${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" = "" ]; then
    echo -e "${RED}Error: Failed to activate virtual environment!${NC}"
    exit 1
fi

echo -e "${GREEN}Virtual environment activated: $VIRTUAL_ENV${NC}"

# Install/update requirements if requirements file exists
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing/updating requirements...${NC}"
    pip install -r requirements.txt
fi

# Set environment variables for display (needed for GUI applications)
export DISPLAY=:0.0

# Run the Python application
echo -e "${GREEN}Starting Python application...${NC}"
echo -e "${YELLOW}Running: python main.py${NC}"

# Run with error handling
python main.py

# Check exit status
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Application completed successfully.${NC}"
else
    echo -e "${RED}Application exited with error code: $EXIT_CODE${NC}"
fi

# Deactivate virtual environment
deactivate

echo -e "${GREEN}Script completed.${NC}" 