#!/bin/bash

# Raspberry Pi Installation Script for Spark SAS2 Application
# This script sets up all dependencies and the virtual environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please run this script as a regular user, not as root!"
        print_warning "The script will ask for sudo password when needed."
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_step "Updating system packages..."
    sudo apt update
    if [ $? -ne 0 ]; then
        print_error "Failed to update package lists"
        exit 1
    fi
    
    sudo apt upgrade -y
    if [ $? -ne 0 ]; then
        print_warning "Some packages failed to upgrade, continuing..."
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    # Core system packages
    SYSTEM_PACKAGES=(
        python3
        python3-pip
        python3-venv
        python3-dev
        python3-setuptools
        build-essential
        git
        curl
        wget
        vim
        htop
    )
    
    # Serial communication dependencies
    SERIAL_PACKAGES=(
        minicom
        screen
        setserial
    )
    
    # Cryptography and security dependencies
    CRYPTO_PACKAGES=(
        libffi-dev
        libssl-dev
        libcrypto++-dev
        pkg-config
        libcairo2-dev
        libjpeg-dev
        libgif-dev
        librsvg2-dev
    )
    
    # Combine all packages
    ALL_PACKAGES=("${SYSTEM_PACKAGES[@]}" "${SERIAL_PACKAGES[@]}" "${CRYPTO_PACKAGES[@]}")
    
    print_status "Installing: ${ALL_PACKAGES[*]}"
    sudo apt install -y "${ALL_PACKAGES[@]}"
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install some system packages"
        exit 1
    fi
    
    print_status "System dependencies installed successfully"
}

# Function to setup serial port permissions
setup_serial_permissions() {
    print_step "Setting up serial port permissions..."
    
    # Add user to dialout group for serial port access
    sudo usermod -a -G dialout "$USER"
    
    if [ $? -eq 0 ]; then
        print_status "Added user '$USER' to 'dialout' group"
        print_warning "You may need to log out and log back in for group changes to take effect"
    else
        print_error "Failed to add user to dialout group"
    fi
}

# Function to create and setup virtual environment
setup_venv() {
    print_step "Setting up Python virtual environment..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # Remove existing virtual environment if it exists
    if [ -d ".venv" ]; then
        print_warning "Existing virtual environment found. Removing..."
        rm -rf .venv
    fi
    
    # Create new virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    if [ "$VIRTUAL_ENV" = "" ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_status "Virtual environment created and activated: $VIRTUAL_ENV"
    
    # Upgrade pip, setuptools, and wheel
    print_status "Upgrading pip, setuptools, and wheel..."
    pip install --upgrade pip setuptools wheel
    
    if [ $? -ne 0 ]; then
        print_warning "Failed to upgrade some Python packages, continuing..."
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt file not found!"
        exit 1
    fi
    
    # Install requirements
    print_status "Installing packages from requirements.txt..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install Python dependencies"
        print_warning "Trying to install packages individually..."
        
        # Try installing packages one by one
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi
            
            print_status "Installing: $line"
            pip install "$line"
            
            if [ $? -ne 0 ]; then
                print_warning "Failed to install: $line"
            fi
        done < requirements.txt
    fi
    
    print_status "Python dependencies installation completed"
}

# Function to verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        print_warning "main.py not found in current directory"
    else
        print_status "main.py found"
    fi
    
    # Check if virtual environment is working
    if [ "$VIRTUAL_ENV" != "" ]; then
        print_status "Virtual environment is active"
        
        # Check key packages
        python -c "import fastapi; print('FastAPI:', fastapi.__version__)" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_status "FastAPI is installed and importable"
        else
            print_warning "FastAPI import failed"
        fi
        
        python -c "import serial; print('PySerial:', serial.__version__)" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_status "PySerial is installed and importable"
        else
            print_warning "PySerial import failed"
        fi
        
        python -c "import uvicorn; print('Uvicorn version check passed')" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_status "Uvicorn is installed and importable"
        else
            print_warning "Uvicorn import failed"
        fi
    fi
    
    # Check serial ports
    if ls /dev/ttyUSB* 1> /dev/null 2>&1; then
        print_status "USB serial ports found: $(ls /dev/ttyUSB*)"
    else
        print_warning "No USB serial ports found (this is normal if no devices are connected)"
    fi
    
    if ls /dev/ttyACM* 1> /dev/null 2>&1; then
        print_status "ACM serial ports found: $(ls /dev/ttyACM*)"
    else
        print_warning "No ACM serial ports found (this is normal if no devices are connected)"
    fi
}

# Function to create startup service (optional)
create_service() {
    print_step "Creating systemd service (optional)..."
    
    read -p "Do you want to create a systemd service for auto-start? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        SERVICE_FILE="/etc/systemd/system/spark-sas2.service"
        CURRENT_DIR="$(pwd)"
        CURRENT_USER="$(whoami)"
        
        print_status "Creating systemd service..."
        
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Spark SAS2 Application
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/.venv/bin
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        if [ $? -eq 0 ]; then
            print_status "Service file created: $SERVICE_FILE"
            
            # Reload systemd and enable service
            sudo systemctl daemon-reload
            sudo systemctl enable spark-sas2.service
            
            print_status "Service enabled. You can control it with:"
            echo "  sudo systemctl start spark-sas2"
            echo "  sudo systemctl stop spark-sas2"
            echo "  sudo systemctl status spark-sas2"
            echo "  sudo journalctl -u spark-sas2 -f"
        else
            print_error "Failed to create service file"
        fi
    else
        print_status "Skipping service creation"
    fi
}

# Function to display final instructions
display_instructions() {
    print_step "Installation Summary"
    
    echo -e "${GREEN}✓ System packages installed${NC}"
    echo -e "${GREEN}✓ Python virtual environment created${NC}"
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
    echo -e "${GREEN}✓ Serial port permissions configured${NC}"
    
    echo
    print_status "Installation completed successfully!"
    echo
    print_warning "IMPORTANT NOTES:"
    echo "1. You may need to log out and log back in for serial port permissions to take effect"
    echo "2. To run the application, use: ./run-spark.sh"
    echo "3. To activate the virtual environment manually: source .venv/bin/activate"
    echo "4. To test the API: python run_api.py"
    echo "5. The API will be available at: http://localhost:8000"
    echo "6. API documentation: http://localhost:8000/docs"
    echo
    print_status "Check the logs if you encounter any issues!"
}

# Main installation process
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Spark SAS2 Raspberry Pi Installer               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    check_root
    
    print_status "Starting installation process..."
    print_warning "This script will install system packages and set up the Python environment"
    echo
    
    # Ask for confirmation
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled by user"
        exit 0
    fi
    
    # Run installation steps
    update_system
    install_system_deps
    setup_serial_permissions
    setup_venv
    install_python_deps
    verify_installation
    create_service
    display_instructions
    
    # Deactivate virtual environment
    deactivate 2>/dev/null || true
    
    print_status "Installation script completed!"
}

# Run main function
main "$@" 