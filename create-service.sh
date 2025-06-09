#!/bin/bash

# Script to create systemd service for Spark SAS2 application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Spark SAS2 Systemd Service...${NC}"

# Get current directory and user
CURRENT_DIR="$(pwd)"
CURRENT_USER="$(whoami)"
SERVICE_FILE="/etc/systemd/system/spark-sas2.service"

# If running as root, get the actual owner of the current directory
if [ "$CURRENT_USER" = "root" ]; then
    ACTUAL_USER=$(stat -c '%U' "$CURRENT_DIR")
    echo -e "${YELLOW}Running as root, but directory is owned by: $ACTUAL_USER${NC}"
    echo -e "${YELLOW}Service will run as: $ACTUAL_USER${NC}"
    CURRENT_USER="$ACTUAL_USER"
fi

echo -e "${YELLOW}Service will be created for:${NC}"
echo "  User: $CURRENT_USER"
echo "  Directory: $CURRENT_DIR"
echo "  Service file: $SERVICE_FILE"
echo

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found in current directory!${NC}"
    exit 1
fi

# Check virtual environment and determine Python path
PYTHON_EXEC=""
UVICORN_EXEC=""

if [ -d ".venv" ] && [ -f ".venv/bin/python" ]; then
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    
    # Test if virtual environment works
    if .venv/bin/python -c "import sys; print('Python works')" 2>/dev/null; then
        echo -e "${GREEN}✓ Virtual environment Python is working${NC}"
        
        # Check if uvicorn is installed in venv
        if [ -f ".venv/bin/uvicorn" ]; then
            echo -e "${GREEN}✓ Uvicorn found in virtual environment${NC}"
            PYTHON_EXEC="$CURRENT_DIR/.venv/bin/python"
            UVICORN_EXEC="$CURRENT_DIR/.venv/bin/uvicorn"
        else
            echo -e "${YELLOW}⚠️  Uvicorn not found in venv, installing...${NC}"
            .venv/bin/pip install uvicorn
            if [ -f ".venv/bin/uvicorn" ]; then
                PYTHON_EXEC="$CURRENT_DIR/.venv/bin/python"
                UVICORN_EXEC="$CURRENT_DIR/.venv/bin/uvicorn"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Virtual environment Python not working${NC}"
    fi
fi

# Fall back to system Python if virtual environment doesn't work
if [ -z "$PYTHON_EXEC" ]; then
    echo -e "${YELLOW}Using system Python as fallback...${NC}"
    
    # Check if system uvicorn exists
    if command -v uvicorn >/dev/null 2>&1; then
        echo -e "${GREEN}✓ System uvicorn found${NC}"
        PYTHON_EXEC="$(which python3)"
        UVICORN_EXEC="$(which uvicorn)"
    else
        echo -e "${YELLOW}⚠️  Installing uvicorn system-wide...${NC}"
        pip3 install uvicorn fastapi
        if command -v uvicorn >/dev/null 2>&1; then
            PYTHON_EXEC="$(which python3)"
            UVICORN_EXEC="$(which uvicorn)"
        else
            echo -e "${RED}Error: Cannot install or find uvicorn!${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}Using:${NC}"
echo "  Python: $PYTHON_EXEC"
echo "  Uvicorn: $UVICORN_EXEC"

# Fix permissions on virtual environment if needed
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Ensuring proper permissions on virtual environment...${NC}"
    sudo chown -R $CURRENT_USER:$CURRENT_USER .venv
    chmod +x .venv/bin/*
fi

echo

# Create the service file
echo -e "${YELLOW}Creating systemd service file...${NC}"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Spark SAS2 Application - Slot Machine Communication Service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$CURRENT_DIR
Environment=NEXTJS_BASE_URL=
Environment=LOG_LEVEL=INFO
Environment=ENVIRONMENT=production
ExecStart=$UVICORN_EXEC main:app --host 0.0.0.0 --port 8000 --workers 1
StandardOutput=journal
StandardError=journal
SyslogIdentifier=spark-sas2

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$CURRENT_DIR

[Install]
WantedBy=multi-user.target
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Service file created successfully${NC}"
    
    # Reload systemd daemon
    echo -e "${YELLOW}Reloading systemd daemon...${NC}"
    sudo systemctl daemon-reload
    
    # Enable the service
    echo -e "${YELLOW}Enabling service for auto-start...${NC}"
    sudo systemctl enable spark-sas2.service
    
    echo -e "${GREEN}✓ Service enabled successfully${NC}"
    echo
    echo -e "${GREEN}Service Management Commands:${NC}"
    echo "  Start service:    sudo systemctl start spark-sas2"
    echo "  Stop service:     sudo systemctl stop spark-sas2"
    echo "  Restart service:  sudo systemctl restart spark-sas2"
    echo "  Check status:     sudo systemctl status spark-sas2"
    echo "  View logs:        sudo journalctl -u spark-sas2 -f"
    echo "  Disable service:  sudo systemctl disable spark-sas2"
    echo
    echo -e "${YELLOW}To start the service now, run:${NC}"
    echo "  sudo systemctl start spark-sas2"
    
else
    echo -e "${RED}✗ Failed to create service file${NC}"
    exit 1
fi 