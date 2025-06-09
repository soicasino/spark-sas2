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

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment (.venv) not found!${NC}"
    echo -e "${YELLOW}Please run the install script first or create venv manually${NC}"
    exit 1
fi

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
Environment=PATH=$CURRENT_DIR/.venv/bin
Environment=PYTHONPATH=$CURRENT_DIR
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/main.py
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